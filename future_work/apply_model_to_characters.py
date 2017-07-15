#!/usr/bin/env python3

# apply_model_to_all_characters.py

# There was already an apply_pickled_model function in
# versatile_trainer, but it was designed to work with
# folders of files, and this will be easier if we use
# the tabular data

import numpy as np
import pandas as pd
import csv, os, random, sys, datetime, pickle
from collections import Counter
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import modelingprocess
import metafilter
import metautils

csv.field_size_limit(sys.maxsize)

forbidden = {'he', 'she', 'her', 'him', 'manhood', 'womanhood', 'boyhood', 'girlhood', 'husband', 'wife', 'lordship', 'ladyship', 'man', 'woman', 'mistress', 'daughter', 'son', 'girl', 'boy', 'bride', 'fiancé', 'fiancée', 'brother', 'sister', 'lady', 'gentleman'}

def get_model(amodelpath):
    with open(amodelpath, 'rb') as input:
        modeldict = pickle.load(input)

    return modeldict

def apply_pickled_model(modeldict, masterdata):
    '''
    Loads a model pickled by the export_model() function above, and applies it to
    a group of texts. Returns a pandas dataframe with a new column for the
    predictions created by this model. The model name becomes the column name.
    This allows us to build up a metadata file with columns for the predictions
    made by multiple models.
    '''
    model = modeldict['itself']
    scaler = modeldict['scaler']

    standarddata = scaler.transform(masterdata)
    probabilities = [x[1] for x in model.predict_proba(standarddata)]

    return probabilities

def write_a_chunk(chunk, metarows, modeldict, outpath, no_header_yet):
    fieldnames = ['docid', 'charid', 'gender', 'pubdate', 'numwords', 'probability']
    masterdata = pd.DataFrame(chunk)
    probabilities = apply_pickled_model(modeldict, masterdata)

    with open(outpath, mode = 'a', encoding = 'utf-8') as f2:
        writer = csv.DictWriter(f2, fieldnames = fieldnames, delimiter = '\t')
        if no_header_yet:
            writer.writeheader()
            no_header_yet = False
        for row, prob in zip(metarows, probabilities):
            row['probability'] = prob
            writer.writerow(row)

    return no_header_yet

def cycle_through(inpath, modeldict, outpath, no_header_yet):

    global forbidden

    vocabulary = modeldict['vocabulary']
    numwords = len(vocabulary)
    vocabmap = dict()
    for i, w in enumerate(vocabulary):
        vocabmap[w] = i
    ctr = 0

    with open(inpath, encoding = 'utf-8') as f1:
        reader = csv.DictReader(f1, delimiter = '\t')
        chunk = []
        metarows = []
        for row in reader:
            newrow = dict()
            newrow['docid'] = row['docid']
            newrow['charid'] = row['charid']
            newrow['gender'] = row['gender']
            newrow['pubdate'] = row['pubdate']
            words = row['words']

            words = row['words'].split(' ')

            if len(words) < 5:
                continue
            # we're ignoring minor characters

            newrow['numwords'] = len(words)
            wordctr = Counter()
            wordtotal = 0
            for w in words:
                if w not in forbidden and not w.startswith('said-'):
                    wordctr[w] += 1
                    wordtotal += 1

            if wordtotal < 5:
                continue

            wordvec = np.zeros(numwords)
            for w, count in wordctr.items():
                if w in vocabmap:
                    idx = vocabmap[w]
                    wordvec[idx] = count / wordtotal

            chunk.append(wordvec)
            metarows.append(newrow)

            if len(chunk) > 1000:
                no_header_yet = write_a_chunk(chunk, metarows, modeldict, outpath, no_header_yet)
                chunk = []
                metarows = []
                print('writing ' + str(ctr))
                ctr += 1

        # catch the last chunk
        if len(chunk) > 0:
            write_a_chunk(chunk, metarows, modeldict, outpath, no_header_yet)

    return no_header_yet

# MAIN

no_header_yet = True

modeldict = get_model('/Users/tunder/Dropbox/python/character/models/wholetimeline.pkl')

inpath = '/Users/tunder/Dropbox/python/character/data/character_table_18c19c.tsv'
outpath = '/Users/tunder/Dropbox/python/character/data/character_probabilities.tsv'

no_header_yet = cycle_through(inpath, modeldict, outpath, no_header_yet)

inpath = '/Users/tunder/Dropbox/python/character/data/character_table_post1900.tsv'

no_header_yet = cycle_through(inpath, modeldict, outpath, no_header_yet)


