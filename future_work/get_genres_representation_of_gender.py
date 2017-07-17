#!/usr/bin/env python3

# This script is designed to apply a particular model of
# gender to characters in a particular span of time,
# and record the predicted probabilities.

# It summarizes and records the predicted probabilities
# both at the author level and at the "story" (document)
# level. In this dataset, some 19c stories include more
# than one volume.

import csv, os, sys
import pandas as pd
import numpy as np

from collections import Counter

import SonicScrewdriver as utils

outdir = 'output'

# LOAD DATA

def normalize_title(title):
    if '/' in title:
        title = title.split('/')[0]
    if '|' in title:
        title = title.split('|')[0]
    title = title.strip('. ,;')

    return title

genremeta = dict()
fallbackdocids = dict()

with open('rawgenredata.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        normalizedauth = row['author'].strip('[](),. ')
        if len(normalizedauth) > 20:
            normalizedauth = normalizedauth[0:20]

        key = (row['author'], normalize_title(row['title']), normalizedauth)
        value = (row['pubdate'], row['genre'], row['authgender'])
        genremeta[key] = value
        fallbackdocids[key] = row['volid']

def match(targetauth, targettitle, possibleauth, possibletitle):
    if possibleauth in aliases:
        possibleauth = aliases[possibleauth]

    possibleauth = possibleauth.strip('[](),. ')
    if len(possibleauth )> 20:
        possibleauth = possibleauth[0:20]

    if len(targettitle) > 15:
        targettitle = targettitle[0:15]
    if len(possibletitle) > 15:
        possibletitle = possibletitle[0:15]

    if targetauth.lower() == possibleauth.lower() and targettitle.lower() == possibletitle.lower():
        return True
    else:
        return False

# Read in aliasfile:
aliases = dict()
with open('genre_aliases_in_filteredfic.tsv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f, delimiter = '\t')
    for row in reader:
        aliases[row['alias']] = row['ourname']

# find matches

key2docid = dict()
volbackup = dict()

with open('../metadata/filtered_fiction_plus_18c.tsv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f, delimiter = '\t')
    for row in reader:

        try:
            intval = int(row['docid'])
            docid = row['docid']
        except:
            docid = utils.clean_pairtree(row['docid'])

        possibleauth = row['author']
        possibletitle = normalize_title(row['title'])
        found = False
        for key, value in genremeta.items():
            author, title, normauth = key
            if match(normauth, title, possibleauth, possibletitle):
                key2docid[key] = docid
                volbackup[key] = utils.clean_pairtree(row['volid'])
                found = True
                print('Found: ', possibleauth, author, possibletitle)
                break

print('Found a total of ', len(key2docid))

for key, docid in fallbackdocids.items():
    if key not in key2docid and docid in fallbackdocids:
        print("adding ", key)
        key2docid[key] = docid

# now let's get all the characters for each story

data = pd.read_csv('prestige_character_probabilities.tsv', sep = '\t', dtype = {'docid': 'object'})
#loads characters

storyout = []

ctr = 0
for key, docid in key2docid.items():
    author, thistitle, normalizedauth = key
    pubdate, genre, authgender = genremeta[key]

    ctr += 1
    print(ctr)

    story_probs = dict()
    story_genders = Counter()
    story_words = Counter()
    storymeta = dict()    # initialize the output record

    chars = data.loc[(data.docid == docid) & (data.numwords > 10), : ]

    if len(chars.pubdate) < 1:
        volid = volbackup[key]
        chars = data.loc[(data.docid == volid) & (data.numwords > 10), : ]

    if len(chars.pubdate) > 0:

        charsizes = chars.numwords
        undifferentiated_probs = chars.probability
        femininechars = chars.loc[chars.gender == 'f', : ]
        masculinechars = chars.loc[chars.gender == 'm', : ]
        story_genders['f'] = len(femininechars.index)
        story_genders['m'] = len(masculinechars.index)
        story_words['f'] = np.sum(femininechars.numwords)
        story_words['m'] = np.sum(masculinechars.numwords)
        story_probs['f'] = femininechars.probability
        story_probs['m'] = masculinechars.probability

    else:
        continue

    prob_mean = np.mean(undifferentiated_probs)

    if story_genders['f'] > 0 and story_genders['m'] > 0:
        prob_diff = np.mean(story_probs['f']) - np.mean(story_probs['m'])
        weighted_diff = np.average(femininechars.probability, weights = femininechars.numwords) - np.average(masculinechars.probability, weights = masculinechars.numwords)
    else:
        prob_diff = float('nan')
        weighted_diff = float('nan')

    prob_stdev = np.std(undifferentiated_probs)

    if (story_words['f'] + story_words['m']) > 0:
        wordratio = story_words['f'] / (story_words['f'] + story_words['m'])
        charratio = story_genders['f'] / (story_genders['f'] + story_genders['m'])
    else:
        wordratio = float('nan')
        charratio = float('nan')

    charsize_mean = np.mean(charsizes)


    storymeta['prob_mean'] = prob_mean

    storymeta['prob_stdev'] = prob_stdev

    storymeta['prob_diff'] = prob_diff
    storymeta['weighted_diff'] = weighted_diff
    storymeta['wordratio'] = wordratio

    storymeta['pct_women'] = charratio

    storymeta['charsize'] = charsize_mean

    storymeta['numchars'] = len(charsizes)

    storymeta['author'] = author
    storymeta['title'] = thistitle
    storymeta['authgender'] = authgender
    storymeta['docid'] = docid
    storymeta['genre'] = genre
    storymeta['pubdate'] = pubdate

    storyout.append(storymeta)


storycolumns = ['docid', 'author', 'title', 'authgender', 'pubdate', 'genre', 'numchars', 'charsize', 'pct_women', 'wordratio','prob_diff', 'weighted_diff', 'prob_stdev', 'prob_mean']

outpath = os.path.join(outdir, 'genre_storymeta.tsv')
with open(outpath, mode = 'w', encoding = 'utf-8') as f:
    writer = csv.DictWriter(f, delimiter = '\t', fieldnames = storycolumns)
    writer.writeheader()
    for s in storyout:
        writer.writerow(s)














