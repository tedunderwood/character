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

    sizecap = 1000

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

    sizecap = 1000

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

def applymodel():
    modelpath = input('Path to model? ')
    sourcefolder = '/Users/tunder/Dropbox/GenreProject/python/reception/fiction/fromEF'
    extension = '.tsv'
    metadatapath = '/Users/tunder/Dropbox/GenreProject/python/reception/fiction/prestigeficmeta.csv'
    newmetadict = train.apply_pickled_model(modelpath, sourcefolder, extension, metadatapath)
    print('Got predictions for that model.')
    outpath = '/Users/tunder/Dropbox/GenreProject/python/reception/poetryEF/mergedmeta.csv'
    newmetadict.to_csv(outpath)

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

    metapath = '../metadata/balanced_speechless_subset.csv'
    sourcefolder = '/Users/tunder/data/speechless_characters/'

    if command == 'optimize_general_model':

        c_range = [.00004, .00009, .0002, .0004, .0008, .0012, .002, .004, .008, .012, 0.3, 0.8, 2]
        featurestart = 1800
        featureend = 3000
        featurestep = 100

        generalmetapath, general_docids = select_subset_to_model('wholetimeline', metapath,
            numexamples = 800, startdate = 1780, enddate = 2010)

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

    else:
        print("I don't know that command.")
