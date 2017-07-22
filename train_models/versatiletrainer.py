#!/usr/bin/env python3

# versatiletrainer.py
#
# Based on logisticpredict, which was based on (!)
# logisticleave1out.py which was based on (!!)
# parallel_crossvalidate.py from the paceofchange repo.
#
# The goal of the module is to construct predictive
# models of corpus *subsets*, in a very flexible way.
# This is necessary because my literary-historical
# interest in modeling is very rarely just
# "model everything and see what we get." I usually
# want to model chronological subsets, or experiment
# with different definitions of classes, or apply a
# model trained on subset A to subset B.
#
# Three problems in particular have to be solved:
#
# a) multilabel modeling
#
# I'm likely to have a corpus where each text bears
# several different class tags. The groups of texts
# identified by class tags will often overlap, and this
# can make it tricky to define positive and negative classes
# for a given modeling pass. Our goal is to ensure
# that no volumes with a positive tag are present in
# the negative class. At the same time,
#
# b) balancing distributions across time
#
# It is vital to ensure that the positive and negative
# classes have similar distributions across
# the timeline. Otherwise you will *definitely* get
# a model that is partly a model of language change.
# Other metadata categories (nationality and gender)
# might also need to be balanced across the positive
# and negative classes, if/when possible.
#
# finally, c) holding out authors
#
# If you just treat volumes as individuals and select a
# test set as a random sample, information about authors can
# leak from test into training, and give you unrealistically
# high accuracy. (You're learning to recognize Radcliffe, not
# learning to recognize the Gothic.) To avoid this, we make sure
# that groups of volumes by the same author are always in the same
# "fold" of crossvalidation.
#
# (Note that the success of this strategy depends on a previous
# fuzzy-matching pass across the corpus to make sure that authors
# have precisely the same name in every row, without extra initials
# or commas, etc).
#
# Much of the work I've just described is handled by
# the function get_data_for_model(), in this module, and inside
# the module *metafilter*, which it calls.
#
# Because we want to be very versatile, there are unfortunately
# a lot of arguments for get_data_for_model(). We pass in three tuples,
# each of which unpacks into a bunch of arguments.
#
# paths unpacks into
# sourcefolder, extension, metadatapath, outputpath, vocabpath
# where
# sourcefolder is the directory with data files
# extension is the extension those files end with
# metadatapath is the path to a metadata csv
# outputpath is the path to a csv of results to be written
# and vocabpath is the path to a file of words to be used
#   as features for all models
#
# exclusions unpacks into
# excludeif, excludeifnot, excludebelow, excludeabove, sizecap
# where
# all the "excludes" are dictionaries pairing a key (the name of a metadata
#     column) with a value that should be excluded -- if it's present,
#     absent, lower than this, or higher than this.
# sizecap limits the number of vols in the positive class; randomly
#      sampled if greater.
#
# classifyconditions unpacks into:
# positive_tags, negative_tags, datetype, numfeatures, regularization, testconditions
# where
# positive_tags is a list of tags to be included in the positive class
# negative_tags is a list of tags to be selected for the negative class
#     (unless volume also has a positive_tag, and note that the negative class
#      is always selected to match the chronological distribution of the positive
#      as closely as possible)
# datetype is the date column to be used for chronological distribution
# numfeatures can be used to limit the features in this model to top N;
#      it is in practice not functional right now because I'm using all
#      features in the vocab file -- originally selected by doc frequency in
#      the whole corpus
# regularization is a constant to be handed to scikit-learn (I'm using one
#    established in previous experiments on a different corpus)
# and testconditions ... is complex.
#
# The variable testconditions will be a set of tags. It may contain tags for classes
# that are to be treated as a test set. Positive volumes will be assigned to
# this set if they have no positive tags that are *not* in testconditions.
# A corresponding group of negative volumes will at the same time
# be assigned. It can also contain two integers to be interpreted as dates, a
# pastthreshold and futurethreshold. Dates outside these thresholds will not
# be used for training. If date thresholds are provided they must be provided
# as a pair to clarify which one is the pastthreshold and which the future.
# If you're only wanting to exclude volumes in the future, provide a past
# threshold like "1."

# All of these conditions exclude volumes from the training set, and place them
# in a set that is used only for testing. But also note that these
# exclusions are always IN ADDITION TO holding-out-authors.

# In other words, if an author w/ multiple volumes has only some of them excluded
# from training by testconditions, it is *still* the case that the author will never
# be in a training set when her own volumes are being predicted.

import numpy as np
import pandas as pd
import csv, os, random, sys, datetime, pickle
from collections import Counter
from multiprocessing import Pool
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

import matplotlib.pyplot as plt

import modelingprocess
import metafilter
import metautils

usedate = False
# Leave this flag false unless you plan major
# surgery to reactivate the currently-deprecated
# option to use "date" as a predictive feature.

includespecialfeatures = True

# this allows punctuation marks, bigrams, and
# statistical metrics to function as features

# FUNCTIONS GET DEFINED BELOW.

def get_features(wordcounts, wordlist):
    numwords = len(wordlist)
    wordvec = np.zeros(numwords)
    for idx, word in enumerate(wordlist):
        if word in wordcounts:
            wordvec[idx] = wordcounts[word]

    return wordvec

def sliceframe(dataframe, yvals, excludedrows, testrow):
    numrows = len(dataframe)
    newyvals = list(yvals)
    for i in excludedrows:
        del newyvals[i]
        # NB: This only works if we assume that excluded rows
        # has already been sorted in descending order !!!!!!!

    trainingset = dataframe.drop(dataframe.index[excludedrows])

    newyvals = np.array(newyvals)
    testset = dataframe.iloc[testrow]

    return trainingset, newyvals, testset

def normalizearray(featurearray, usedate):
    '''Normalizes an array by centering on means and
    scaling by standard deviations. Also returns the
    means and standard deviations for features, so that
    they can be pickled.
    '''

    numinstances, numfeatures = featurearray.shape
    means = list()
    stdevs = list()
    lastcolumn = numfeatures - 1
    for featureidx in range(numfeatures):

        thiscolumn = featurearray.iloc[ : , featureidx]
        thismean = np.mean(thiscolumn)

        thisstdev = np.std(thiscolumn)

        if (not usedate) or featureidx != lastcolumn:
            # If we're using date we don't normalize the last column.
            means.append(thismean)
            stdevs.append(thisstdev)
            featurearray.iloc[ : , featureidx] = (thiscolumn - thismean) / thisstdev
        else:
            print('FLAG')
            means.append(thismean)
            thisstdev = 0.1
            stdevs.append(thisstdev)
            featurearray.iloc[ : , featureidx] = (thiscolumn - thismean) / thisstdev
            # We set a small stdev for date.

    return featurearray, means, stdevs

def confirm_testconditions(testconditions, positive_tags):

    for elem in testconditions:
        if elem in positive_tags or elem.isdigit():
            # that's fine
            continue
        elif elem == '':
            # also okay
            continue
        elif elem == 'donotmatch':
            print("You have instructed me that positive volumes matching only a")
            print("positive tag in the test-but-not-train group should not be matched")
            print("with negative volumes.")
        elif elem.startswith('limit=='):
            limit = elem.replace('limit==', '')
            print()
            print("You have instructed me to allow only "+ limit)
            print("volumes in the do-not-train set.")
            print()
        else:
            print('Illegal element in testconditions.')
            sys.exit(0)

def get_thresholds(testconditions):
    ''' The testconditions are a set of elements that may include dates
    (setting an upper and lower limit for training, outside of which
    volumes are only to be in the test set), or may include genre tags.

    This function only identifies the dates, if present. If not present,
    it returns 0 and 3000. Do not use this code for predicting volumes
    dated after 3000 AD. At that point, the whole thing is deprecated.
    '''

    thresholds = []
    for elem in testconditions:
        if elem.isdigit():
            thresholds.append(int(elem))

    thresholds.sort()
    if len(thresholds) == 2:
        pastthreshold = thresholds[0]
        futurethreshold = thresholds[1]
    else:
        pastthreshold = 0
        futurethreshold = 3000
        # we are unlikely to have any volumes before or after
        # those dates

    return pastthreshold, futurethreshold

def get_volume_lists(volumeIDs, volumepaths, IDsToUse):
    '''
    This function creates an ordered list of volume IDs included in this
    modeling process, and an ordered list of volume-path tuples.

    It also identifies positive volumes that are not to be included in a training set,
    because they belong to a category that is being tested.
    '''

    volspresent = []
    orderedIDs = []

    for volid, volpath in zip(volumeIDs, volumepaths):
        if volid not in IDsToUse:
            continue
        else:
            volspresent.append((volid, volpath))
            orderedIDs.append(volid)

    return volspresent, orderedIDs

def first_and_last(idset, metadict, datetype):
    min = 3000
    max = 0

    for anid in idset:
        date = metadict[anid][datetype]
        if date < min:
            min = date
        if date > max:
            max = date

    return min, max

def describe_donttrainset(donttrainset, classdictionary, metadict, datetype):

    positivedonts = []
    negativedonts = []

    for anid in donttrainset:
        posneg = classdictionary[anid]
        if posneg == 0:
            negativedonts.append(anid)
        elif posneg == 1:
            positivedonts.append(anid)
        else:
            print('Anomaly in classdictionary.')

    min, max = first_and_last(positivedonts, metadict, datetype)
    if min > 0:
        print("The set of volumes not to be trained on includes " + str(len(positivedonts)))
        print("positive volumes, ranging from " + str(min) + " to " + str(max) + ".")
        print()

    min, max = first_and_last(negativedonts, metadict, datetype)
    if min > 0:
        print("And also includes " + str(len(negativedonts)))
        print("negative volumes, ranging from " + str(min) + " to " + str(max) + ".")
        print()

def record_trainflags(metadict, donttrainset):
    ''' This function records, for each volume, whether it is or is not
    to be used in training. Important to run it after add_matching_negs so
    that we know which volumes in the negative set were or weren't used
    in training.
    '''

    for docid, metadata in metadict.items():
        if docid in donttrainset:
            metadata['trainflag'] = 0
        else:
            metadata['trainflag'] = 1

def make_vocablist(volspresent, n, vocabpath):
    '''
    Makes a list of the top n words in sourcedir, and writes it
    to vocabpath.
    '''

    global includespecialfeatures

    sourcepaths = [x[1] for x in volspresent]
    # volspresent is a list of id, path 2-tuples created by get_volume_lists

    wordcounts = Counter()

    for path in sourcepaths:

        with open(path, encoding = 'utf-8') as f:
            for line in f:
                fields = line.strip().split('\t')
                if len(fields) > 2 or len(fields) < 2:
                    continue
                if fields[1] != 'frequency':
                    word = fields[0]
                    if len(word) > 0 and not word.startswith('#bi_'):
                        wordcounts[word] += 1

    with open(vocabpath, mode = 'w', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['word', 'docfreq'])
        for word, count in wordcounts.most_common(n):
            writer.writerow([word, count])

    vocabulary = [x[0] for x in wordcounts.most_common(n)]

    return vocabulary

def get_vocablist(vocabpath, volspresent, useall, n):
    '''
    Gets the vocablist stored in vocabpath or, alternately, if that list
    doesn't yet exist, it creates a vocablist and puts it there.
    '''

    vocablist = []
    ctr = 0

    if not os.path.isfile(vocabpath):
        vocablist = make_vocablist(volspresent, n, vocabpath)
    else:
        with open(vocabpath, encoding = 'utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ctr += 1
                if ctr > n:
                    break
                    # this allows us to limit how deep we go

                word = row['word']
                count = int(row['docfreq'])
                if count > 1 or useall:
                    vocablist.append(word)

        if len(vocablist) > n:
            vocablist = vocablist[0: n]

    return vocablist

def get_docfrequency(volspresent, donttrainset):
    '''
    This function counts words in volumes. These wordcounts don't necessarily define
    a feature set for modeling: at present, the limits of that set are defined primarily
    by a fixed list shared across all models (top10k).
    '''

    wordcounts = Counter()

    for volid, volpath in volspresent:
        if volid in donttrainset:
            continue
        else:
            with open(volpath, encoding = 'utf-8') as f:
                for line in f:
                    fields = line.strip().split('\t')
                    if len(fields) > 2 or len(fields) < 2:
                        # this is a malformed line; there are a few of them,
                        # but not enough to be important -- ignore
                        continue
                    word = fields[0]
                    if len(word) > 0 and word[0].isalpha():
                        wordcounts[word] += 1
                        # We're getting docfrequency (the number of documents that
                        # contain this word), not absolute number of word occurrences.
                        # So just add 1 no matter how many times the word occurs.

    return wordcounts

def model_call(quintuplets, algorithm):
    '''
    Invokes multiprocessing to distribute n-fold crossvalidation
    simultaneously across multiple threads. Since I'm usually doing this
    on a computer with 12 cores, I set 12 threads.
    '''

    print('Beginning multiprocessing.')
    pool = Pool(processes = 12)

    if algorithm == 'logistic':
        res = pool.map_async(modelingprocess.model_volume_list, quintuplets)
    else:
        res = pool.map_async(modelingprocess.svm_model, quintuplets)

    # After all files are processed, write metadata, errorlog, and counts of phrases.
    res.wait()
    resultlist = res.get()
    pool.close()
    pool.join()
    print('Multiprocessing concluded.')

    return resultlist

def crossvalidate(data, classvector, folds, algorithm, regu_const):
    '''
    Creates a set of tuples that can be sent to a multiprocessing Pool,
    one "quintuplet" for each thread.
    '''
    quintuplets = list()
    foldindices = []
    for fold in folds:
        foldindices, foldids = tuple(zip(*fold))
        foldindices = list(foldindices)
        foldids = list(foldids)
        # we package each fold as a zipped list of numeric-index, id pairs

        aquintuple = data, classvector, foldids, foldindices, regu_const
        quintuplets.append(aquintuple)

    # Now do crossvalidation.
    resultlist = model_call(quintuplets, algorithm)

    assert len(resultlist) == len(folds)

    predictions = dict()
    for results, fold in zip(resultlist, folds):
        assert len(results) == len(fold)
        foldindices, foldids = tuple(zip(*fold))
        for r, volid in zip(results, foldids):
            predictions[volid] = r

    return predictions

def calculate_accuracy(orderedIDs, predictions, classdictionary, donttrainset, verbose):
    '''
    What it says on the tin.
    '''

    truepositives = 0
    truenegatives = 0
    falsepositives = 0
    falsenegatives = 0
    totalcount = 0

    for volid in orderedIDs:

        if volid in donttrainset:
            continue
        totalcount += 1

        # The donttrainset contains volids that are *only* ever
        # being predicted, and do not appear in the training set for
        # any fold of crossvalidation.

        # We're not going to count the donttrainset in assessing
        # accuracy during gridsearch, because we're not trying to
        # *optimize* on it.

        probability = predictions[volid]
        realclass = classdictionary[volid]

        if probability > 0.5 and classdictionary[volid] > 0.5:
            truepositives += 1
        elif probability <= 0.5 and classdictionary[volid] < 0.5:
            truenegatives += 1
        elif probability <= 0.5 and classdictionary[volid] > 0.5:
            falsenegatives += 1
        elif probability > 0.5 and classdictionary[volid] < 0.5:
            falsepositives += 1

    print()

    accuracy = (truepositives + truenegatives) / totalcount

    if verbose:
        print('True positives ' + str(truepositives))
        print('True negatives ' + str(truenegatives))
        print('False positives ' + str(falsepositives))
        print('False negatives ' + str(falsenegatives))
        precision = truepositives / (truepositives + falsepositives)
        recall = truepositives / (truepositives + falsenegatives)
        F1 = 2 * (precision * recall) / (precision + recall)
        print("F1 : " + str(F1))

    return accuracy

def gridsearch(featurestart, featureend, featurestep, c_range, masterdata, orderedIDs, folds, algorithm, classdictionary, classvector, donttrainset):
    '''
    Does a grid search cross a range of feature counts and
    C values. The assumption is that we're always taking the top
    x words in the vocabulary.

    Note that the matrix will actually display with the "x axis"
    on the side, and the "y axis" at the bottom. Sorry!
    '''

    xaxis = [x for x in range(featurestart, featureend, featurestep)]
    yaxis = c_range

    xlen = len(xaxis)
    ylen = len(yaxis)
    matrix = np.zeros((xlen, ylen))

    for xpos, variablecount in enumerate(xaxis):
        data = masterdata.iloc[ : , 0 : variablecount]

        for ypos, regu_const in enumerate(yaxis):

            print('variablecount: ' + str(variablecount) + "  regularization: " + str(regu_const))

            predictions = crossvalidate(data, classvector, folds, algorithm, regu_const)


            accuracy = calculate_accuracy(orderedIDs, predictions, classdictionary, donttrainset, False)
            print('Accuracy: ' + str(accuracy))
            print()
            matrix[xpos, ypos] = accuracy

    plt.rcParams["figure.figsize"] = [9.0, 6.0]
    plt.matshow(matrix, origin = 'lower', cmap = plt.cm.YlOrRd)
    plt.show()

    coords = np.unravel_index(matrix.argmax(), matrix.shape)
    print(coords)
    print(xaxis[coords[0]], yaxis[coords[1]])
    features4max = xaxis[coords[0]]
    c4max = yaxis[coords[1]]

    return matrix, features4max, c4max, matrix.max()

def create_folds(k, orderedIDs, authormatches, classdictionary):
    '''
    Does k-fold crossvalidation. Returns a list of "folds," which will
    be a list of lists [ [], [], [], etc. ],
    where each sublist is a list of two-tuples (), (), ()
    of which the first element is the index of a volume in orderedIDs,
    and the second element the volume ID itself.
    '''

    folds = [[] for x in range(k)]
    # e.g. k == 10 will produce: [[], [], [], [], [], [], [], [], [], []]

    assignedinclass = dict()
    assignedinclass[0] = [0 for x in range(k)]
    assignedinclass[1] = [0 for x in range(k)]

    # we make an effort to keep the classes balanced across folds


    ids_to_distribute = set(orderedIDs)
    nextbin = 0

    randomizedtuples = list(zip(list(range(len(orderedIDs))), orderedIDs))
    random.shuffle(randomizedtuples)

    for i, anid in randomizedtuples:
        if anid in ids_to_distribute:
            classlabel = classdictionary[anid]
            thisclasscounts = assignedinclass[classlabel]
            ascending = sorted(thisclasscounts)
            whichlowest = thisclasscounts.index(ascending[0])

            nextbin = whichlowest

            folds[nextbin].append((i, anid))
            assignedinclass[classlabel][nextbin] += 1
            ids_to_distribute.remove(anid)

            for anotheridx in authormatches[i]:
                if anotheridx == i:
                    continue
                    # for some reason I've made everything a member
                    # of its own authormatch list

                anotherid = orderedIDs[anotheridx]
                folds[nextbin].append((anotheridx, anotherid))
                classlabel = classdictionary[anotherid]
                assignedinclass[classlabel][nextbin] += 1

                if anotherid in ids_to_distribute:
                    ids_to_distribute.remove(anotherid)
                    # but notice, we assign anotherid even if it has already
                    # been assigned elsewhere; all the donottrain volumes
                    # need to be in all folds

    print(assignedinclass[0])
    print(assignedinclass[1])

    return folds

def leave_one_out_folds(orderedIDs, authormatches, classdictionary):
    '''
    Makes folds for leave-one-out crossvalidation.
    '''

    folds = []
    alreadyassigned = set()

    # our strategy is to create folds only if they contain an index
    # not already assigned

    for matchlist in authormatches:
        allassigned = True
        for idx in matchlist:
            if idx not in alreadyassigned:
                allassigned = False

        if not allassigned:
            afold = [(x, orderedIDs[x]) for x in matchlist]
            folds.append(afold)
            for item in matchlist:
                alreadyassigned.add(item)

    # confirm we got everything

    print([len(x) for x in folds])
    print(len(folds))

    assert alreadyassigned == set(range(len(orderedIDs)))

    return folds

def get_dataframe(metadict, volspresent, classdictionary, vocablist, freqs_already_normalized):
    '''
    Given a vocabulary list, and list of volumes, this actually creates the
    pandas dataframe with volumes as rows and words (or other features) as
    columns. It also enriches the metadata dictionary with information about
    total wordcount for each volume.
    '''

    voldata = list()
    classvector = list()

    for volid, volpath in volspresent:

        with open(volpath, encoding = 'utf-8') as f:
            voldict = dict()
            totalcount = 0
            for line in f:
                fields = line.strip().split('\t')
                if len(fields) > 2 or len(fields) < 2:
                    continue

                word = fields[0]
                if fields[1] == 'frequency':
                    continue
                count = float(fields[1])
                voldict[word] = count
                totalcount += count

        features = get_features(voldict, vocablist)
        if totalcount == 0:
            totalcount = .00001
        if freqs_already_normalized:
            voldata.append(features)
        else:
            voldata.append(features / totalcount)

        metadict[volid]['volsize'] = totalcount
        classflag = classdictionary[volid]
        classvector.append(classflag)

    masterdata = pd.DataFrame(voldata)

    return masterdata, classvector, metadict

def get_data_for_model(paths, exclusions, classifyconditions):
    ''' Unpacks a bunch of parameters that define metadata
    conditions for positive and negative classes. Finds volumes
    meeting those conditions, creates a lexicon if one doesn't
    already exist, and creates a pandas dataframe storing
    texts as rows and words/features as columns.
    '''

    sourcefolder, extension, metadatapath, outputpath, vocabpath = paths
    excludeif, excludeifnot, excludebelow, excludeabove, sizecap = exclusions
    positive_tags, negative_tags, datetype, numfeatures, regularization, testconditions = classifyconditions

    verbose = False
    holdout_authors = True

    # If you want reliable results, always run this with holdout_authors
    # set to True. The only reason to set it to False is to confirm that
    # this flag is actually making a difference. If you do that, it
    # disables the code that keeps other works by the author being predicted
    # out of the training set.

    freqs_already_normalized = True

    # By default we assume that frequencies have already been normalized
    # (divided by the total number of words in the volume). This allows us
    # to use some features (like type/token ratio) that would become
    # meaningless if divided by total wordcount. But it means that I'm
    # offloading some important feature-engineering decisions to the
    # data prep stage.

    # The following function confirms that the testconditions are legal.

    confirm_testconditions(testconditions, positive_tags)

    if not sourcefolder.endswith('/'):
        sourcefolder = sourcefolder + '/'

    # This just makes things easier.

    # Get a list of files.
    allthefiles = os.listdir(sourcefolder)

    # RANDOMNESS.

    # random.shuffle(allthefiles)

    # RANDOMNESS. This is an important line. Without it, you'd get the same sequence of
    # orderedIDs each time, and the same distribution of IDs into folds of the cross-
    # validation

    volumeIDs = list()
    volumepaths = list()

    for filename in allthefiles:

        if filename.endswith(extension):
            volID = filename.replace(extension, "")
            # The volume ID is basically the filename minus its extension.
            # Extensions are likely to be long enough that there is little
            # danger of accidental occurrence inside a filename. E.g.
            # '.fic.tsv'
            path = sourcefolder + filename
            volumeIDs.append(volID)
            volumepaths.append(path)

    metadict = metafilter.get_metadata(metadatapath, volumeIDs, excludeif, excludeifnot, excludebelow, excludeabove)

    # Now that we have a list of volumes with metadata, we can select the groups of IDs
    # that we actually intend to contrast.

    if type(positive_tags[0]).__name__ == 'int':
        categorytodivide = 'firstpub'
    else:
        categorytodivide = 'tagset'

    IDsToUse, classdictionary, donttrainset = metafilter.label_classes(metadict, categorytodivide, positive_tags, negative_tags, sizecap, datetype, excludeif, testconditions)

    print()
    min, max = first_and_last(IDsToUse, metadict, datetype)
    if min > 0:
        print("The whole corpus involved here includes " + str(len(IDsToUse)))
        print("volumes, ranging in date from " + str(min) + " to " + str(max) + ".")
        print()

    # We now create an ordered list of id-path tuples for later use, and identify a set of
    # positive ids that should never be used in training.

    volspresent, orderedIDs = get_volume_lists(volumeIDs, volumepaths, IDsToUse)

    # Extend the set of ids not to be used in training by identifying negative volumes that match
    # the distribution of positive volumes.

    describe_donttrainset(donttrainset, classdictionary, metadict, datetype)

    # Create a flag for each volume that indicates whether it was used in training

    record_trainflags(metadict, donttrainset)

    # Get a count of docfrequency for all words in the corpus. This is probably not needed and
    # might be deprecated later.

    # wordcounts = get_docfrequency(volspresent, donttrainset)

    # The feature list we use is defined by the top 10,000 words (by document
    # frequency) in the whole corpus, and it will be the same for all models.

    vocablist = get_vocablist(vocabpath, volspresent, useall = True, n = numfeatures)

    # This function either gets the vocabulary list already stored in vocabpath, or
    # creates a list of the top 10k words in all files, and stores it there.
    # N is a parameter that could be altered right here.

    # Useall is a parameter that you basically don't need to worry about unless
    # you're changing / testing code. If you set it to false, the vocablist will
    # exclude words that occur very rarely. This shouldn't be necessary; the
    # crossvalidation routine is designed not to include features that occur
    # zero times in the training set. But if you get div-by-zero errors in the
    # training process, you could fiddle with this parameter as part of a
    # troubleshooting process.

    numfeatures = len(vocablist)
    print()
    print("Number of features " + str(numfeatures))

    # For each volume, we're going to create a list of volumes that should be
    # excluded from the training set when it is to be predicted. More precisely,
    # we're going to create a list of their *indexes*, so that we can easily
    # remove rows from the training matrix.

    # This list will include for ALL volumes, the indexes of vols in the donttrainset.

    donttrainon = [orderedIDs.index(x) for x in donttrainset]

    authormatches = [list(donttrainon) for x in range(len(orderedIDs))]

    # Now we proceed to enlarge that list by identifying, for each volume,
    # a set of indexes that have the same author. Obvs, there will always be at least one.
    # We exclude a vol from it's own training set.

    if holdout_authors:
        for idx1, anid in enumerate(orderedIDs):
            thisauthor = metadict[anid]['author']
            for idx2, anotherid in enumerate(orderedIDs):
                otherauthor = metadict[anotherid]['author']
                if thisauthor == otherauthor and not idx2 in authormatches[idx1]:
                    authormatches[idx1].append(idx2)
    else:
        # This code only runs if we're testing the effect of
        # holdout_authors by disabling it.

        for idx1, anid in enumerate(orderedIDs):
            if idx1 not in authormatches[idx1]:
                authormatches[idx1].append(idx1)


    # The purpose of everything that follows is to
    # balance negative and positive instances in each
    # training set.

    trainingpositives = set()
    trainingnegatives = set()

    for anid, thisclass in classdictionary.items():
        if anid in donttrainset:
            continue

        if thisclass == 1:
            trainingpositives.add(orderedIDs.index(anid))
        else:
            trainingnegatives.add(orderedIDs.index(anid))

    print('Training positives: ' + str(len(trainingpositives)))
    print('Training negatives: ' + str(len(trainingnegatives)))


    for alist in authormatches:
        alist.sort(reverse = True)

    # I am reversing the order of indexes so that I can delete them from
    # back to front, without changing indexes yet to be deleted.
    # This will become important in the modelingprocess module.

    masterdata, classvector, metadict = get_dataframe(metadict, volspresent, classdictionary, vocablist, freqs_already_normalized)

    return metadict, masterdata, classvector, classdictionary, orderedIDs, donttrainon, donttrainset, authormatches, vocablist

def get_fullmodel(data, classvector, donttrainon, vocablist, regularization):
    '''
    Instead of crossvalidating (producing multiple models),
    this function runs a single model on the whole set.
    '''

    trainingset, yvals, testset = sliceframe(data, classvector, donttrainon, 0)
    trainingset, testset = modelingprocess.remove_zerocols(trainingset, testset)
    newmodel = LogisticRegression(C = regularization)

    stdscaler = StandardScaler()
    stdscaler.fit(trainingset)
    scaledtraining = stdscaler.transform(trainingset)

    newmodel.fit(scaledtraining, yvals)

    coefficients = newmodel.coef_[0] * 100

    coefficientuples = list(zip(coefficients, (coefficients / stdscaler.var_), vocablist))
    coefficientuples.sort()

    return coefficientuples, newmodel, stdscaler

def export_model(modelitself, algorithm, scaler, vocabulary, positive_tags, negative_tags, c, n, outpath):
    '''
    Creates a dictionary with spots for a scikit-learn model and associated data objects that will
    be needed to apply it to texts. E.g., a vocabulary, which tells you which words occupy which
    columns, and a StandardScaler object, which stores the means and variances needed to normalize
    your data (convert frequencies to z scores). Other useful metadata is also stored; the whole
    dictionary is picked and written to file.
    '''
    model = dict()
    model['vocabulary'] = vocabulary
    model['itself'] = modelitself
    model['algorithm'] = algorithm
    model['scaler'] = scaler
    model['positivelabel'] = positive_tags
    model['negativelabel'] = negative_tags
    model['c'] = c
    model['n'] = n
    modelname = outpath.split('/')[-1].replace('.pkl', '')
    model['name'] = modelname
    with open(outpath, 'wb') as output:
        pickle.dump(model, output)

def apply_pickled_model(amodelpath, folder, extension, metapath):
    '''
    Loads a model pickled by the export_model() function above, and applies it to
    a new folder of texts. Returns a pandas dataframe with a new column for the
    predictions created by this model. The model name becomes the column name.
    This allows us to build up a metadata file with columns for the predictions
    made by multiple models.
    '''
    with open(amodelpath, 'rb') as input:
        modeldict = pickle.load(input)

    vocablist = modeldict['vocabulary']
    algorithm = modeldict['algorithm']
    model = modeldict['itself']
    scaler = modeldict['scaler']
    modelname = modeldict['name']

    metadata = pd.read_csv(metapath)
    metadata = metadata.set_index(['docid'])
    metadata = metadata[~metadata.index.duplicated(keep='first')]

    volspresent = []
    classdictionary = dict()
    metadict = dict()
    # classdictionary is going to be a dummy parameter where everything is
    # the same class, since we don't actually need to do any training.
    # metadict is also a dummy parameter.
    resultindex = []

    for doc in metadata.index:
        inpath = os.path.join(folder, doc + extension)
        if os.path.exists(inpath):
            volspresent.append( (doc, inpath) )
            classdictionary[doc] = 0
            metadict[doc] = dict()
            resultindex.append(doc)
        else:
            print(inpath)

    print(len(volspresent))

    masterdata, classvector, metadict = get_dataframe(metadict, volspresent, classdictionary, vocablist, True)
    # True, there, means frequencies already normalized to be relative freqs.
    print(masterdata.shape)

    standarddata = scaler.transform(masterdata)
    probabilities = [x[1] for x in model.predict_proba(standarddata)]

    # we create a column named for the model
    probabilities = pd.Series(probabilities, index = resultindex)
    # we index the results using the volumes we actually found

    metadata['logistic'] = probabilities
    # indexes will automatically align, putting NaN for any vols
    # not found

    return metadata

def tune_a_model(paths, exclusions, classifyconditions, modelparams):
    '''
    This has become the central workhorse class in the module. It takes
    a set of parameters defining positive and negative subsets of a corpus,
    and gathers data for those subsets.

    Then it runs a grid search, modeling the texts using a range of parameters
    defined by modelparams. This involves trying different numbers of features
    while simultaneously varying C. Logistic regression and SVMs are both
    supported as options; the constant C has a different meaning in those two
    algorithms, but the process of tuning parameters is basically analogous.

    After finding the best number of features, and value of C, we run the
    model again using those parameters, to get predicted probabilities
    for volumes. Technically, I suppose we could have saved all
    the predictions from the grid search to avoid this step, but omg, needless
    complexity.

    We also run the model one last time *without* crossvalidation to get
    a list of coefficients and a model object that can be saved to be applied
    to other corpora. For this we invoke get_fullmodel(). We skip crossvalidation
    here in order to get a single model object that reflects the whole training
    set.

    We write coefficients, predictions, and model object to file, using variations
    of the outputpath contained in the "path" tuple.
    '''

    metadata, masterdata, classvector, classdictionary, orderedIDs, donttrainon, donttrainset, authormatches, vocablist = get_data_for_model(paths, exclusions, classifyconditions)

    algorithm, k, featurestart, featureend, featurestep, crange = modelparams
    positive_tags, negative_tags, datetype, numfeatures, regularization, testconditions = classifyconditions

    print(len(orderedIDs))
    print('compare')
    all = []
    for item in authormatches:
        all.extend(item)
    print(len(set(all)))

    # to request leave-one-out crossvalidation, set k to zero
    if k < 1:
        folds = leave_one_out_folds(orderedIDs, authormatches, classdictionary)
    else:
        folds = create_folds(k, orderedIDs, authormatches, classdictionary)


    matrix, features4max, best_regularization_coef, maxaccuracy = gridsearch(featurestart, featureend, featurestep, crange, masterdata, orderedIDs, folds, algorithm, classdictionary, classvector, donttrainset)

    datasubset = masterdata.iloc[ : , 0 : features4max]

    predictions = crossvalidate(datasubset, classvector, folds, algorithm, best_regularization_coef)
    accuracy = calculate_accuracy(orderedIDs, predictions, classdictionary, donttrainset, True)

    print(accuracy, maxaccuracy)
    # those two should be effectively the same

    coefficientuples, fullmodel, scaler = get_fullmodel(datasubset, classvector, donttrainon, vocablist,best_regularization_coef)

    sourcefolder, extension, metadatapath, outputpath, vocabpath = paths

    modelpath = outputpath.replace('.csv', '.pkl')
    export_model(fullmodel, algorithm, scaler, vocablist[0 : features4max], positive_tags, negative_tags,best_regularization_coef, len(orderedIDs), modelpath)

    coefficientpath = outputpath.replace('.csv', '.coefs.csv')
    with open(coefficientpath, mode = 'w', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        for triple in coefficientuples:
            coef, normalizedcoef, word = triple
            writer.writerow([word, coef, normalizedcoef])

    allvolumes = []
    with open(outputpath, mode = 'w', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        header = ['volid', 'dateused', 'pubdate', 'birthdate', 'firstpub', 'gender', 'nation', 'allwords', 'logistic', 'realclass', 'trainflag', 'trainsize', 'author', 'title', 'genretags']
        writer.writerow(header)

        for volid in orderedIDs:
            thisvolume = metadata[volid]
            dateused = thisvolume[datetype]
            pubdate = thisvolume['pubdate']
            birthdate = thisvolume['birthdate']
            firstpub = thisvolume['firstpub']
            gender = thisvolume['gender']
            nation = thisvolume['nation']
            author = thisvolume['author']
            title = thisvolume['title']
            allwords = thisvolume['volsize']
            logistic = predictions[volid]
            realclass = classdictionary[volid]
            trainflag = thisvolume['trainflag']
            genretags = ' | '.join(thisvolume['tagset'])
            outrow = [volid, dateused, pubdate, birthdate, firstpub, gender, nation, allwords, logistic, realclass, trainflag, author, title, genretags]
            writer.writerow(outrow)
            allvolumes.append(outrow)

    return matrix, maxaccuracy, allvolumes, coefficientuples

def crossvalidate_single_model(paths, exclusions, classifyconditions, modelparams):
    '''
    This has become the central workhorse class in the module. It takes
    a set of parameters defining positive and negative subsets of a corpus,
    and gathers data for those subsets.

    Then it runs a grid search, modeling the texts using a range of parameters
    defined by modelparams. This involves trying different numbers of features
    while simultaneously varying C. Logistic regression and SVMs are both
    supported as options; the constant C has a different meaning in those two
    algorithms, but the process of tuning parameters is basically analogous.

    After finding the best number of features, and value of C, we run the
    model again using those parameters, to get predicted probabilities
    for volumes. Technically, I suppose we could have saved all
    the predictions from the grid search to avoid this step, but omg, needless
    complexity.

    We also run the model one last time *without* crossvalidation to get
    a list of coefficients and a model object that can be saved to be applied
    to other corpora. For this we invoke get_fullmodel(). We skip crossvalidation
    here in order to get a single model object that reflects the whole training
    set.

    We write coefficients, predictions, and model object to file, using variations
    of the outputpath contained in the "path" tuple.
    '''

    metadata, masterdata, classvector, classdictionary, orderedIDs, donttrainon, donttrainset, authormatches, vocablist = get_data_for_model(paths, exclusions, classifyconditions)

    algorithm, k, featurestart, featureend, featurestep, crange = modelparams
    positive_tags, negative_tags, datetype, numfeatures, regularization, testconditions = classifyconditions

    print(len(orderedIDs))
    all = []
    for item in authormatches:
        all.extend(item)

    # to request leave-one-out crossvalidation, set k to zero
    if k < 1:
        folds = leave_one_out_folds(orderedIDs, authormatches, classdictionary)
    else:
        folds = create_folds(k, orderedIDs, authormatches, classdictionary)

    assert featurestart == featureend
    # because this is for a known model
    maxfeatures = featurestart

    best_regularization_coef = crange[0]
    # because this is for a known model

    datasubset = masterdata.iloc[ : , 0 : maxfeatures]

    predictions = crossvalidate(datasubset, classvector, folds, algorithm, best_regularization_coef)
    accuracy = calculate_accuracy(orderedIDs, predictions, classdictionary, donttrainset, True)

    print(accuracy)
    # those two should be effectively the same

    coefficientuples, fullmodel, scaler = get_fullmodel(datasubset, classvector, donttrainon, vocablist,best_regularization_coef)

    sourcefolder, extension, metadatapath, outputpath, vocabpath = paths

    modelpath = outputpath.replace('.csv', '.pkl')
    export_model(fullmodel, algorithm, scaler, vocablist[0 : maxfeatures], positive_tags, negative_tags,best_regularization_coef, len(orderedIDs), modelpath)

    coefficientpath = outputpath.replace('.csv', '.coefs.csv')
    with open(coefficientpath, mode = 'w', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        for triple in coefficientuples:
            coef, normalizedcoef, word = triple
            writer.writerow([word, coef, normalizedcoef])

    allvolumes = []
    with open(outputpath, mode = 'w', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        header = ['volid', 'dateused', 'pubdate', 'birthdate', 'firstpub', 'gender', 'nation', 'allwords', 'logistic', 'realclass', 'trainflag', 'trainsize', 'author', 'title', 'genretags']
        writer.writerow(header)

        for volid in orderedIDs:
            thisvolume = metadata[volid]
            dateused = thisvolume[datetype]
            pubdate = thisvolume['pubdate']
            birthdate = thisvolume['birthdate']
            firstpub = thisvolume['firstpub']
            gender = thisvolume['gender']
            nation = thisvolume['nation']
            author = thisvolume['author']
            title = thisvolume['title']
            allwords = thisvolume['volsize']
            logistic = predictions[volid]
            realclass = classdictionary[volid]
            trainflag = thisvolume['trainflag']
            genretags = ' | '.join(thisvolume['tagset'])
            outrow = [volid, dateused, pubdate, birthdate, firstpub, gender, nation, allwords, logistic, realclass, trainflag, author, title, genretags]
            writer.writerow(outrow)
            allvolumes.append(outrow)

    return accuracy, allvolumes, coefficientuples

def diachronic_tilt(allvolumes, modeltype, datelimits):
    ''' Takes a set of predictions produced by a model that knows nothing about date,
    and divides it along a line with a diachronic tilt. We need to do this in a way
    that doesn't violate crossvalidation. I.e., we shouldn't "know" anything
    that the model didn't know. We tried a couple of different ways to do this, but
    the simplest and actually most reliable is to divide the whole dataset along a
    linear central trend line for the data!
    '''

    listofrows = list()
    classvector = list()

    for volume in allvolumes:
        date = volume[1]
        logistic = volume[8]
        realclass = volume[9]
        listofrows.append([logistic, date])
        classvector.append(realclass)

    y, x = [a for a in zip(*listofrows)]
    plt.axis([min(x) - 2, max(x) + 2, min(y) - 0.02, max(y) + 0.02])
    reviewedx = list()
    reviewedy = list()
    randomx = list()
    randomy = list()

    for idx, reviewcode in enumerate(classvector):
        if reviewcode == 1:
            reviewedx.append(x[idx])
            reviewedy.append(y[idx])
        else:
            randomx.append(x[idx])
            randomy.append(y[idx])

    plt.plot(reviewedx, reviewedy, 'ro')
    plt.plot(randomx, randomy, 'k+')

    if modeltype == 'logistic':
        # all this is DEPRECATED
        print("Hey, you're attempting to use the logistic-tilt option")
        print("that we deactivated. Go in and uncomment the code.")

    elif modeltype == 'linear':
        # what we actually do

        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        slope = z[0]
        intercept = z[1]

    plt.plot(x,p(x),"b-")
    plt.show()

    x = np.array(x, dtype='float64')
    y = np.array(y, dtype='float64')
    classvector = np.array(classvector)
    dividingline = intercept + (x * slope)
    predicted_as_reviewed = (y > dividingline)
    really_reviewed = (classvector == 1)

    accuracy = sum(predicted_as_reviewed == really_reviewed) / len(classvector)

    return accuracy

if __name__ == '__main__':

    # If this class is called directly, it creates a single model using the default
    # settings set below.

    ## PATHS.

    # sourcefolder = '/Users/tunder/Dropbox/GenreProject/python/reception/fiction/texts/'
    # extension = '.fic.tsv'
    # metadatapath = '/Users/tunder/Dropbox/GenreProject/python/reception/fiction/masterficmeta.csv'
    # outputpath = '/Users/tunder/Dropbox/GenreProject/python/reception/fiction/predictions.csv'

    sourcefolder = '/Users/tunder/Dropbox/GenreProject/python/reception/fiction/fromEF'
    extension = '.tsv'
    metadatapath = '/Users/tunder/Dropbox/GenreProject/python/reception/fiction/snootymeta.csv'
    vocabpath = '/Users/tunder/Dropbox/GenreProject/python/reception/fiction/lexica/snootyreviews.txt'

    ## modelname = input('Name of model? ')
    modelname = 'snootyreviews1850-1950'

    outputpath = '/Users/tunder/Dropbox/GenreProject/python/reception/fiction/results/' + modelname + '.csv'

    # We can simply exclude volumes from consideration on the basis on any
    # metadata category we want, using the dictionaries defined below.

    ## EXCLUSIONS.

    excludeif = dict()
    excludeifnot = dict()
    excludeabove = dict()
    excludebelow = dict()

    ## daterange = input('Range of dates to use in the model? ')
    daterange = '1850,1950'
    if ',' in daterange:
        dates = [int(x.strip()) for x in daterange.split(',')]
        dates.sort()
        if len(dates) == 2:
            assert dates[0] < dates[1]
            excludebelow['firstpub'] = dates[0]
            excludeabove['firstpub'] = dates[1]

    # allstewgenres = {'cozy', 'hardboiled', 'det100', 'chimyst', 'locdetective', 'lockandkey', 'crime', 'locdetmyst', 'blcrime', 'anatscifi', 'locscifi', 'chiscifi', 'femscifi', 'stangothic', 'pbgothic', 'lochorror', 'chihorror', 'locghost'}
    # excludeif['negatives'] = allstewgenres

    sizecap = 600

    # CLASSIFY CONDITIONS

    # We ask the user for a list of categories to be included in the positive
    # set, as well as a list for the negative set. Default for the negative set
    # is to include all the "random"ly selected categories. Note that random volumes
    # can also be tagged with various specific genre tags; they are included in the
    # negative set only if they lack tags from the positive set.

    ## tagphrase = input("Comma-separated list of tags to include in the positive class: ")
    tagphrase = 'elite'
    positive_tags = [x.strip() for x in tagphrase.split(',')]
    ## tagphrase = input("Comma-separated list of tags to include in the negative class: ")
    tagphrase = 'vulgar'

    # An easy default option.
    if tagphrase == 'r':
        negative_tags = ['random', 'grandom', 'chirandom']
    else:
        negative_tags = [x.strip() for x in tagphrase.split(',')]

    # We also ask the user to specify categories of texts to be used only for testing.
    # These exclusions from training are in addition to ordinary crossvalidation.

    print()
    print("You can also specify positive tags to be excluded from training, and/or a pair")
    print("of integer dates outside of which vols should be excluded from training.")
    print("If you add 'donotmatch' to the list of tags, these volumes will not be")
    print("matched with corresponding negative volumes.")
    print()
    ## testphrase = input("Comma-separated list of such tags: ")
    testphrase = ''
    testconditions = set([x.strip() for x in testphrase.split(',') if len(x) > 0])

    datetype = "firstpub"
    numfeatures = 6000
    regularization = .000075
    # "regularization" has become a dummy parameter, superseded by modelparams below
    # numfeatures, likewise, now only sets the ceiling for gridsearch

    paths = (sourcefolder, extension, metadatapath, outputpath, vocabpath)
    exclusions = (excludeif, excludeifnot, excludebelow, excludeabove, sizecap)
    classifyconditions = (positive_tags, negative_tags, datetype, numfeatures, regularization, testconditions)

    c_range = [.00005, .0001, .0003, .0006, .001, .002, .004, .01, .1, 1]

    # c_range = [.001, .002, .004, .01, .1, 1, 3, 6, 9, 12]

    modelparams = 'logistic', 24, 3000, 6000, 200, c_range
    # this is algorithm, k-fold crossvalidation, ftstart, ftend, ftstep, range for C

    matrix, rawaccuracy, allvolumes, coefficientuples = tune_a_model(paths, exclusions, classifyconditions, modelparams)

    print('If we divide the dataset with a horizontal line at 0.5, accuracy is: ', str(rawaccuracy))
    tiltaccuracy = diachronic_tilt(allvolumes, 'linear', [])

    print("Divided with a line fit to the data trend, it's ", str(tiltaccuracy))

