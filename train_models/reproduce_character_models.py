#!/usr/bin/env python3

# reproduce_character_models.py

# Reproduce predictive modeling of characters.

# This script assumes that you have subset.tar.gz
# in the parent directory of the /train_models directory
# directory. It also expects to have a /temp directory
# as a sibling (at the same level as /train_models).
# When it's asked to create a model it extracts
# characters from the tar.gz file and puts them
# in temp. Inefficient? Yes! But it means I can
# use versatiletrainer without having to edit it
# to take data from a tarfile.

# It also assumes that character metadata is in
# /metadata/balanced_character_subset.csv.

# Finally, it wants a folder '../models', again
# placed as a sibling, where it can put various
# intermediate lexicons and metadata.

import csv, os, sys, pickle, math, tarfile
import versatiletrainer as train
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def select_subset_to_model(modelname, metadatapath, numexamples, startdate, enddate):
    '''
    Creates metadata for a model of gender trained on a balanced
    sample of the whole timeline.

    In keeping with Python practice, the date range is inclusive at the bottom,
    but not the top.

    It returns a path to the metadata created.
    '''

    allmeta = pd.read_csv(metadatapath)
    timeslice = allmeta[(allmeta.firstpub >= startdate) & (allmeta.firstpub < enddate)]
    m = timeslice[timeslice.gender == 'm']
    f = timeslice[timeslice.gender == 'f']
    msample = m.sample(n = numexamples)
    fsample = f.sample(n = numexamples)
    general_sample = pd.concat([msample, fsample])
    outpath = '../models/' + modelname + '_meta.csv'
    general_sample.to_csv(outpath)

    return outpath, general_sample.docid

def authgender_subset_to_model(modelname, agender, metadatapath, numexamples, startdate, enddate):
    '''
    Creates metadata for a subset of characters drawn only from books
    written by authors of a specified gender (agender).

    It returns a path to the metadata created.
    '''

    allmeta = pd.read_csv(metadatapath)
    timeslice = allmeta[(allmeta.authgender == agender) & (allmeta.firstpub >= startdate) & (allmeta.firstpub < enddate)]
    m = timeslice[timeslice.gender == 'm']
    f = timeslice[timeslice.gender == 'f']
    msample = m.sample(n = numexamples)
    fsample = f.sample(n = numexamples)
    general_sample = pd.concat([msample, fsample])
    outpath = '../models/' + modelname + '_meta.csv'
    general_sample.to_csv(outpath)

    return outpath, general_sample.docid

def subset_to_predict_authgender(modelname, metadatapath, num, startdate, enddate):
    '''
    Creates metadata that can be used to actually predict authgender.

    It returns a path to the metadata created.
    '''

    allmeta = pd.read_csv(metadatapath)
    timeslice = allmeta[(allmeta.firstpub >= startdate) & (allmeta.firstpub < enddate)]
    mbym = timeslice[(timeslice.authgender == 'm') & (timeslice.gender == 'm')]
    fbym = timeslice[(timeslice.authgender == 'm') & (timeslice.gender == 'f')]
    mbyf = timeslice[(timeslice.authgender == 'f') & (timeslice.gender == 'm')]
    fbyf = timeslice[(timeslice.authgender == 'f') & (timeslice.gender == 'f')]
    general_sample = pd.concat([mbym.sample(n = num), fbym.sample(n = num),
        mbyf.sample(n = num), fbyf.sample(n = num)])
    outpath = '../models/' + modelname + '_meta.csv'

    general_sample['tags'] = general_sample.authgender
    # that's the line that actually ensures we are predicting
    # author gender rather than character gender

    general_sample.to_csv(outpath)

    return outpath, np.mean(general_sample.firstpub)

def refresh_temp(list_of_docids):
    '''
    Empties the temporary folder and restocks it, using a list
    of docids that are in subset.tar.gz.
    '''

    folder = '../temp'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

    with tarfile.open('../subset.tar.gz', 'r:gz') as tar:
        for d in list_of_docids:
            tarmember = 'charactersubset/' + d + '.tsv'
            destination = '../temp/' + d + '.tsv'
            data = tar.extractfile(tarmember).read().decode('utf-8')
            with open(destination, mode = 'w', encoding = 'utf-8') as f:
                f.write(data)

def gridsearch_a_model(metadatapath, sourcefolder, c_range, ftstart, ftend, ftstep, positive_tags = ['f'], negative_tags = ['m']):
    ''' Function does a gridsearch to identify an optimal number of features and setting of
    the regularization constant; then produces that model. Note that we do not use this for
    models of specific decades. Just initially for model selection.'''

    modelname = metadatapath.replace('.//models/', '').replace('_meta.csv', '')
    extension = '.tsv'
    vocabpath = metadatapath.replace('_meta', '_vocab')
    if os.path.exists(vocabpath):
        print('Vocabulary for ' + modelname + ' already exists. Using it.')
    outputpath = metadatapath.replace('_meta', '')

    ## EXCLUSIONS. # not used in this project

    excludeif = dict()
    excludeifnot = dict()
    excludeabove = dict()
    excludebelow = dict()

    sizecap = 2000

    # CLASSIFY CONDITIONS # not used in this project

    testconditions = set()

    datetype = "firstpub"
    numfeatures = ftend
    regularization = .000075
    # linting the code would get rid of regularization, which is at this
    # point an unused dummy parameter

    paths = (sourcefolder, extension, metadatapath, outputpath, vocabpath)
    exclusions = (excludeif, excludeifnot, excludebelow, excludeabove, sizecap)
    classifyconditions = (positive_tags, negative_tags, datetype, numfeatures, regularization, testconditions)

    modelparams = 'logistic', 12, ftstart, ftend, ftstep, c_range

    matrix, rawaccuracy, allvolumes, coefficientuples = train.tune_a_model(paths, exclusions, classifyconditions, modelparams)

    print('If we divide the dataset with a horizontal line at 0.5, accuracy is: ', str(rawaccuracy))
    tiltaccuracy = train.diachronic_tilt(allvolumes, 'linear', [])

    print("Divided with a line fit to the data trend, it's ", str(tiltaccuracy))

def crossvalidate_one_model(metadatapath, sourcefolder, c_range, ftstart, ftend, ftstep, positive_tags = ['f'], negative_tags = ['m']):
    ''' '''

    modelname = metadatapath.replace('.//models/', '').replace('_meta.csv', '')
    extension = '.tsv'
    vocabpath = metadatapath.replace('_meta', '_vocab')
    if os.path.exists(vocabpath):
        os.unlink(vocabpath)
        # we rebuild vocab each time
    outputpath = metadatapath.replace('_meta', '')

    ## EXCLUSIONS. # not used in this project

    excludeif = dict()
    excludeifnot = dict()
    excludeabove = dict()
    excludebelow = dict()

    sizecap = 2000

    # CLASSIFY CONDITIONS # not used in this project

    testconditions = set()

    datetype = "firstpub"
    numfeatures = ftend
    regularization = .000075
    # linting the code would get rid of regularization, which is at this
    # point an unused dummy parameter

    paths = (sourcefolder, extension, metadatapath, outputpath, vocabpath)
    exclusions = (excludeif, excludeifnot, excludebelow, excludeabove, sizecap)
    classifyconditions = (positive_tags, negative_tags, datetype, numfeatures, regularization, testconditions)

    modelparams = 'logistic', 12, ftstart, ftend, ftstep, c_range

    rawaccuracy, allvolumes, coefficientuples = train.crossvalidate_single_model(paths, exclusions, classifyconditions, modelparams)

    print(rawaccuracy)

    return rawaccuracy

def crossvalidate_across_L2_range(metadatapath, sourcefolder, c_range, ftstart, ftend, ftstep, positive_tags = ['f'], negative_tags = ['m']):
    '''
    For a given set of characters, crossvalidates a model at multiple
    L2 settings, and returns all the accuracies.
    '''

    modelname = metadatapath.replace('.//models/', '').replace('_meta.csv', '')
    extension = '.tsv'
    vocabpath = metadatapath.replace('_meta', '_vocab')
    if os.path.exists(vocabpath):
        os.unlink(vocabpath)
        # we rebuild vocab each time
    outputpath = metadatapath.replace('_meta', '')

    ## EXCLUSIONS. # not used in this project

    excludeif = dict()
    excludeifnot = dict()
    excludeabove = dict()
    excludebelow = dict()

    sizecap = 2000

    # CLASSIFY CONDITIONS # not used in this project

    testconditions = set()

    datetype = "firstpub"
    numfeatures = ftend
    regularization = .000075
    # linting the code would get rid of regularization, which is at this
    # point an unused dummy parameter

    paths = (sourcefolder, extension, metadatapath, outputpath, vocabpath)
    exclusions = (excludeif, excludeifnot, excludebelow, excludeabove, sizecap)
    classifyconditions = (positive_tags, negative_tags, datetype, numfeatures, regularization, testconditions)

    accuracydict = dict()
    for c_setting in c_range:

        cparam = [c_setting]

        modelparams = 'logistic', 10, ftstart, ftend, ftstep, cparam

        rawaccuracy, allvolumes, coefficientuples = train.crossvalidate_single_model(paths, exclusions, classifyconditions, modelparams)

        accuracydict[c_setting] = rawaccuracy

    return accuracydict


def applymodel(modelpath, metapath, outpath):
    ''' This function applies a specified model (modelpath) to a specified
    metadata set (metapath), and sends the results to outpath.
    '''

    sourcefolder = '/Users/tunder/data/character_subset/'
    extension = '.tsv'
    metadatapath = metapath = '../metadata/balanced_character_subset.csv'
    newmetadict = train.apply_pickled_model(modelpath, sourcefolder, extension, metadatapath)
    print('Got predictions for that model.')
    newmetadict.to_csv(outpath)

def correlate_models(firstpath, secondpath):
    one = pd.read_csv(firstpath, index_col = 'docid')
    two = pd.read_csv(secondpath, index_col = 'docid')
    justpredictions = pd.concat([one['logistic'], two['logistic']], axis=1, keys=['one', 'two'])
    justpredictions.dropna(inplace = True)
    r, p = pearsonr(justpredictions.one, justpredictions.two)
    return r

def comparison(selfmodel, othermodel, modelname):

        totalvolumes = 0
        right = 0

        for v in selfmodel.index:
            realgenre = selfmodel.loc[v, 'realclass']
            v = str(v)
            otherprediction = othermodel.loc[v, modelname]
            if realgenre > .5 and otherprediction > 0.5:
                right += 1
            elif realgenre < .5 and otherprediction < 0.5:
                right += 1
            totalvolumes +=1

        return totalvolumes, right

def getacc(filelist):
    allofem = 0
    allright = 0
    for afile in filelist:
        df = pd.read_csv(afile)
        totalcount = len(df.realclass)
        tp = sum((df.realclass > 0.5) & (df.logistic > 0.5))
        tn = sum((df.realclass <= 0.5) & (df.logistic <= 0.5))
        fp = sum((df.realclass <= 0.5) & (df.logistic > 0.5))
        fn = sum((df.realclass > 0.5) & (df.logistic <= 0.5))
        assert totalcount == (tp + fp + tn + fn)
        allofem += totalcount
        allright += (tp + tn)
    return allright / allofem

if __name__ == '__main__':

    args = sys.argv

    command = args[1]

    metapath = '../metadata/balanced_character_subset.csv'
    sourcefolder = '/Users/tunder/data/character_subset/'

    if command == 'optimize_general_model':

        c_range = [.000003, .00001, .00003, .00009, .0003, .0009, .002, .004, .008]
        featurestart = 1000
        featureend = 3200
        featurestep = 100

        generalmetapath, general_docids = select_subset_to_model('wholetimeline', metapath,
            numexamples = 800, startdate = 1780, enddate = 2010)

        gridsearch_a_model(generalmetapath, sourcefolder, c_range,
            featurestart, featureend, featurestep)

    if command == 'optimize_fifty_years':

        # this option creates a model that can be used for comparison to
        # the model of fictional prestige, which spans only 1850-1950

        c_range = [.0001]
        featurestart = 2450
        featureend = 2700
        featurestep = 50

        generalmetapath, general_docids = select_subset_to_model('fiftypost1950', metapath, numexamples = 1500, startdate = 1950, enddate = 2050)

        # The number of examples is higher here, because we want this model to be maximally
        # accurate, and we're not trying to use this as a guide for other 800-character
        # models.

        gridsearch_a_model(generalmetapath, sourcefolder, c_range,
            featurestart, featureend, featurestep)

    elif command == 'test_decades':

        c_range = [.0004]
        featurestart = 2300
        featureend = 2300
        featurestep = 100

        with open('../dataforR/speechlessdecademodels.tsv', mode = 'w', encoding = 'utf-8') as f:
            f.write('decade\taccuracy\n')
            for dec in range (1790, 2010, 10):
                if dec == 1790:
                    floor = 1780
                    ceiling = 1800
                else:
                    floor = dec
                    ceiling = dec + 10

                modelname = 'decade' + str(dec)
                for i in range(15):
                    decademetapath, docids = select_subset_to_model(modelname, metapath, numexamples = 800,
                        startdate = floor, enddate = ceiling)
                    accuracy = crossvalidate_one_model(decademetapath, sourcefolder, c_range, featurestart, featureend, featurestep)
                    f.write(str(dec) + '\t' + str(accuracy) + '\n')

    elif command == 'optimize_20c':
        c_range = [.000003, .00001, .00003, .00009, .0003, .0009, .002, .004, .008]
        featurestart = 1100
        featureend = 3000
        featurestep = 100

        generalmetapath, general_docids = select_subset_to_model('wholetwentieth', metapath,
            numexamples = 800, startdate = 1900, enddate = 2000)

        gridsearch_a_model(generalmetapath, sourcefolder, c_range,
            featurestart, featureend, featurestep)

    elif command == 'optimize_19c':
        c_range = [.000003, .00001, .00003, .00009, .0003, .0009, .002, .004, .008]
        featurestart = 1100
        featureend = 3000
        featurestep = 100

        generalmetapath, general_docids = select_subset_to_model('wholenineteenth', metapath,
            numexamples = 800, startdate = 1800, enddate = 1900)

        gridsearch_a_model(generalmetapath, sourcefolder, c_range,
            featurestart, featureend, featurestep)

    elif command == 'optimize_thirty':
        decade = int(args[2])
        c_range = [.000003, .00001, .00003, .00009, .0003, .0009, .002, .004, .008]
        featurestart = 1900
        featureend = 3000
        featurestep = 100
        modelname = 'optimalthirty' + str(decade)
        generalmetapath, general_docids = select_subset_to_model(modelname, metapath,
            numexamples = 1500, startdate = decade - 10, enddate = decade + 20)

        gridsearch_a_model(generalmetapath, sourcefolder, c_range,
            featurestart, featureend, featurestep)

    elif command == 'decade_grid':

        # This is the function I finally used. Keeps the number of features
        # fixed at 2200, but generates a new lexicon for each decade (and each
        # sample of 800 characters within the decade). Tests each decade at
        # multiple L2 settings, and records them all, so we can take the
        # optimal setting but also figure out how much of a difference that's
        # making.

        c_range = [.00003, .0001, .0003, .001]
        featurestart = 2200
        featureend = 2200
        featurestep = 100

        with open('../dataforR/decadegrid.tsv', mode = 'w', encoding = 'utf-8') as f:
            f.write('decade\tL2\taccuracy\titer\n')
            for dec in range (1790, 2010, 10):
                if dec == 1790:
                    floor = 1780
                    ceiling = 1800
                else:
                    floor = dec
                    ceiling = dec + 10

                modelname = 'decade' + str(dec)
                for i in range(15):
                    decademetapath, docids = select_subset_to_model(modelname, metapath, numexamples = 800,
                        startdate = floor, enddate = ceiling)
                    accuracydict = crossvalidate_across_L2_range(decademetapath, sourcefolder, c_range, featurestart, featureend, featurestep)
                    for L2setting, accuracy in accuracydict.items():
                        f.write(str(dec) + '\t' + str(L2setting) + '\t' + str(accuracy) + '\t' + str(i) + '\n')

    elif command == 'decade_grid_for_differentiation_plot':

        # This is the function I finally used. Keeps the number of features
        # fixed at 2200, but generates a new lexicon for each decade (and each
        # sample of 800 characters within the decade). Tests each decade at
        # multiple L2 settings, and records them all, so we can take the
        # optimal setting but also figure out how much of a difference that's
        # making.

        c_range = [.0001]
        featurestart = 2300
        featureend = 2300
        featurestep = 100


        for dec in range (1790, 2010, 10):
            floor = dec - 10
            ceiling = dec + 20

            modelname = 'thirty' + str(dec)
            decademetapath, docids = select_subset_to_model(modelname, metapath, numexamples = 1500,
                startdate = floor, enddate = ceiling)
            accuracy = crossvalidate_one_model(decademetapath, sourcefolder, c_range, featurestart, featureend, featurestep)
            print(str(dec) + '\t' + str(accuracy) + '\n')

    elif command == 'auth_specific_charpredict_grid':

        # This is the function I finally used. Keeps the number of features
        # fixed at 2200, but generates a new lexicon for each decade (and each
        # sample of 800 characters within the decade). Tests each decade at
        # multiple L2 settings, and records them all, so we can take the
        # optimal setting but also figure out how much of a difference that's
        # making.

        c_range = [.00003, .0001, .0003, .001]
        featurestart = 2200
        featureend = 2200
        featurestep = 100

        metapath = '../metadata/balanced_authgender_subset.csv'
        sourcefolder = '/Users/tunder/data/authgender_subset/'

        with open('../dataforR/auth_specific_charpredict.tsv', mode = 'w', encoding = 'utf-8') as f:
            f.write('decade\tauthgender\tL2\taccuracy\titer\n')
            for dec in range (1800, 2000, 20):
                if dec == 1790:
                    floor = 1780
                    ceiling = 1800
                else:
                    floor = dec
                    ceiling = dec + 20


                for agender in ['m', 'f']:
                    modelname = agender + 'author' + '_' + str(dec)
                    for i in range(5):
                        decademetapath, docids = authgender_subset_to_model(modelname, agender, metapath, numexamples = 800,
                            startdate = floor, enddate = ceiling)
                        accuracydict = crossvalidate_across_L2_range(decademetapath, sourcefolder, c_range, featurestart, featureend, featurestep)
                        for L2setting, accuracy in accuracydict.items():
                            f.write(str(dec) + '\t' + agender + '\t' + str(L2setting) + '\t' + str(accuracy) + '\t' + str(i) + '\n')

    elif command == 'predict_authgender':

        # This is the function I finally used. Keeps the number of features
        # fixed at 2200, but generates a new lexicon for each decade (and each
        # sample of 800 characters within the decade). Tests each decade at
        # multiple L2 settings, and records them all, so we can take the
        # optimal setting but also figure out how much of a difference that's
        # making.

        c_range = [.0001, .0003, .001, .003]
        featurestart = 2500
        featureend = 2500
        featurestep = 100

        metapath = '../metadata/balanced_authgender_subset.csv'
        sourcefolder = '/Users/tunder/data/authgender_subset/'

        with open('../dataforR/authgender_predictions.tsv', mode = 'w', encoding = 'utf-8') as f:
            f.write('meandate\tL2\taccuracy\titer\n')
            for dec in range (1795, 2010, 17):
                if dec == 1790:
                    floor = 1780
                    ceiling = 1800
                else:
                    floor = dec
                    ceiling = dec + 17

                modelname = 'predict_authgender' + '_' + str(dec)
                for i in range(9):
                    decademetapath, meandate = subset_to_predict_authgender(modelname, metapath, num = 400,
                        startdate = floor, enddate = ceiling)
                    # note that in this case num is not the total number of male or female examples,
                    # but the number for each cell of a 2x2 contingency matrix of author gender
                    # versus character gender so 400 produces 1600 total instances

                    accuracydict = crossvalidate_across_L2_range(decademetapath, sourcefolder, c_range, featurestart, featureend, featurestep)
                    for L2setting, accuracy in accuracydict.items():
                        f.write(str(meandate) + '\t' + str(L2setting) + '\t' + str(accuracy) + '\t' + str(i) + '\n')

    elif command == 'optimize_authgender':

        c_range = [.000003, .00001, .00003, .00009, .0003, .0009, .002, .004, .008, .03, 1]
        featurestart = 800
        featureend = 3600
        featurestep = 100

        metapath = '../metadata/balanced_authgender_subset.csv'
        sourcefolder = '/Users/tunder/data/authgender_subset/'

        generalmetapath, general_docids = subset_to_predict_authgender('general_authgender', metapath,
            num = 400, startdate = 1780, enddate = 2010)

        gridsearch_a_model(generalmetapath, sourcefolder, c_range,
            featurestart, featureend, featurestep)

    elif command == 'onlywomenwriters':

        c_range = [.0003]
        featurestart = 2500
        featureend = 2600
        featurestep = 100

        womensmetapath, docids = authgender_subset_to_model('onlywomenwritersC', 'f', metapath, numexamples = 1500, startdate = 1800, enddate = 2000)

        gridsearch_a_model(womensmetapath, sourcefolder, c_range, featurestart, featureend, featurestep)

    elif command == 'onlymalewriters':

        c_range = [.0003]
        featurestart = 2500
        featureend = 2600
        featurestep = 100

        womensmetapath, docids = authgender_subset_to_model('onlymalewritersC', 'm', metapath, numexamples = 1500, startdate = 1800, enddate = 2000)

        gridsearch_a_model(womensmetapath, sourcefolder, c_range, featurestart, featureend, featurestep)

    elif command == 'compare_models':
        men = ['onlymalewriters', 'onlymalewritersB', 'onlymalewritersC']
        women = ['onlywomenwriters', 'onlywomenwritersB', 'onlywomenwritersC']
        # test_subset_path, test_docids = select_subset_to_model('test_metadata', metapath, numexamples = 1000, startdate = 1800, enddate = 2000)
        test_subset_path = '../models/test_metadata_meta.csv'
        generaloutpath = '/Users/tunder/Dropbox/python/character/future_work/appliedmodels/'
        masculineperspective = []
        feminineperspective = []
        for m in men:
            modelpath = '../models/' + m + '.pkl'
            outpath = generaloutpath + m + '.results'
            if not os.path.exists(outpath):
                applymodel(modelpath, test_subset_path, outpath)
            masculineperspective.append(outpath)
        for w in women:
            modelpath = '../models/' + w + '.pkl'
            outpath = generaloutpath + w + '.results'
            if not os.path.exists(outpath):
                applymodel(modelpath, test_subset_path, outpath)
            feminineperspective.append(outpath)
        print('among men:')
        r = []
        r.append(correlate_models(masculineperspective[0], masculineperspective[1]))
        r.append(correlate_models(masculineperspective[1], masculineperspective[2]))
        r.append(correlate_models(masculineperspective[0], masculineperspective[2]))
        print(sum(r) / len(r))
        print('among women:')
        r = []
        r.append(correlate_models(feminineperspective[0], feminineperspective[1]))
        r.append(correlate_models(feminineperspective[1], feminineperspective[2]))
        r.append(correlate_models(feminineperspective[0], feminineperspective[2]))
        print(sum(r) / len(r))
        print('between genders:')
        r = []
        r.append(correlate_models(masculineperspective[0], feminineperspective[0]))
        r.append(correlate_models(masculineperspective[1], feminineperspective[0]))
        r.append(correlate_models(masculineperspective[1], feminineperspective[1]))
        r.append(correlate_models(masculineperspective[1], feminineperspective[2]))
        r.append(correlate_models(masculineperspective[0], feminineperspective[2]))
        r.append(correlate_models(masculineperspective[2], feminineperspective[2]))
        print(sum(r) / len(r))

    else:
        print("I don't know that command.")
