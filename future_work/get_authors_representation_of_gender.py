#!/usr/bin/env python3

# This script is designed to apply a particular model of
# gender to characters in a particular span of time,
# and record the predicted probabilities.

# It summarizes and records the predicted probabilities
# both at the author level and at the "story" (document)
# level. In this dataset, some 19c stories include more
# than one volume.

# USAGE:

# python3 get_authors_representation_of_gender.py source.csv genderprobs.tsv outdir

# source.csv       a csv like fiction_prestige_results.csv
# genderprobs.tsv  a probability file created by apply_model_to_characters.py
#                  in my data th is called character_probabilities.tsv
# outdir           a folder, in which storymeta.tsv and authormeta.tsv files
#                  will be created

# DEPENDENCIES:
# it expects SonicScrewdriver.py and aliasfile.tsv to be in the
# same directory.

# it also expects an enlarged version of filtered_fiction_metadata
# (one that includes vols 1780-1799) to be in a sibling "metadata"
# directory, as it is in the repo

import csv, os, sys
import pandas as pd
import numpy as np

from collections import Counter

# import utils
# currentdir = os.path.dirname(__file__)
# sys.path.append(currentdir)

import SonicScrewdriver as utils

# UNPACK ARGUMENTS

args = sys.argv
if len(args) < 4:
    print('This script expects three arguments.')
    print('See usage instructions in the code.')
    sys.exit(0)

prestige_source_path = args[1]
gender_prob_path = args[2]
outdir = args[3]

# LOAD DATA

prestige = pd.read_csv(prestige_source_path)
metadata = pd.read_csv('../metadata/filtered_fiction_plus_18c.tsv', sep ='\t')

metadata['volid'] = metadata.volid.apply(utils.clean_pairtree)

# Read in aliasfile:
aliases = dict()
with open('aliasfile.tsv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f, delimiter = '\t')
    for row in reader:
        aliases[row['alias']] = row['ourname']

with open('aliases_in_filteredfic.tsv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f, delimiter = '\t')
    for row in reader:
        aliases[row['alias']] = row['ourname']

# Let's start by identifying all stories in our metadata by
# authors in the prestige dataset.

# Author names can vary. So first, we're going to apply
# a translation function that converts various aliases
# into "ourname" -- a name present in the metadata file.

# then we strip punctuation, trim to 25 chars, kill periods
# after initials, and lowercase, to increase matches.

def translate_aliases(aname):
    global aliases
    if type(aname) != str:
        return 'Anonymous'

    if aname in aliases:
        return aliases[aname]
    elif aname.strip(',.) ]') in aliases:
        return aliases[aname.strip(',.) ]')]
    else:
        return aname

def trim_to_24(aname):
    if type(aname) != str:
        return 'Anonymous'

    aname = aname.strip('(),. .[0123456789]')
    if len (aname) > 24:
        return aname[0:24]
    else:
        return aname

known_authors = set([trim_to_24(a) for a in prestige.author])
prestige['trimmedauth'] = prestige.author.apply(trim_to_24)

metadata['trimmedauth'] = metadata.author.apply(translate_aliases)
metadata['trimmedauth'] = metadata.trimmedauth.apply(trim_to_24)
all_matches = set(metadata.trimmedauth)

auth2story = dict()
auth2gender = dict()
auth_prestige_means = dict()
auth_sales_means = dict()

for a in known_authors:
    if a in all_matches:
        stories = metadata.loc[metadata.trimmedauth == a, 'docid']
        auth2story[a] = list(set(stories))
        authgender = metadata.loc[metadata.trimmedauth == a, 'authgender']
        if len(authgender) > 0:
            authgender = authgender.iloc[0]
            auth2gender[a] = authgender

    auth_prestige_means[a] = np.mean(prestige.loc[prestige.trimmedauth == a, 'prestige'])
    auth_sales_means[a] = np.mean(prestige.loc[prestige.trimmedauth == a, 'percentile'])


# now let's get all the characters for each story
print('Authors found:')
print(len(auth2story))

data = pd.read_csv(gender_prob_path, sep = '\t', dtype = {'docid': 'object'})
#loads characters

storydates = dict()
authorout = []
storyout = []

ctr = 0
for a in known_authors:
    auth_prob_means = []
    auth_prob_diffs = []
    auth_charratios = []
    auth_wordratios = []
    auth_prob_stdev = []
    auth_charsize_means = []
    auth_num_chars = []
    auth_dates = []
    auth_weighted_diffs = []

    if a in auth2story:
        ctr += 1
        print(ctr)
        stories = auth2story[a]

        for s in stories:
            story_probs = dict()
            story_genders = Counter()
            story_words = Counter()
            storymeta = dict()    # initialize the output record
            thistitle = metadata.loc[metadata.docid == s, 'title'].iloc[0]

            chars = data.loc[(data.docid == s) & (data.numwords > 10), : ]
            if len(chars.pubdate) > 0:

                charsizes = chars.numwords
                undifferentiated_probs = chars.probability
                storymeta['pubdate'] = chars.pubdate.iloc[0]
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
            auth_prob_means.append(prob_mean)
            storymeta['prob_stdev'] = prob_stdev
            auth_prob_stdev.append(prob_stdev)
            storymeta['prob_diff'] = prob_diff
            auth_prob_diffs.append(prob_diff)
            storymeta['weighted_diff'] = weighted_diff
            auth_weighted_diffs.append(weighted_diff)
            storymeta['wordratio'] = wordratio
            auth_wordratios.append(wordratio)
            storymeta['pct_women'] = charratio
            auth_charratios.append(charratio)
            storymeta['charsize'] = charsize_mean
            auth_charsize_means.append(charsize_mean)
            storymeta['numchars'] = len(charsizes)
            auth_num_chars.append(len(charsizes))
            storymeta['author'] = a
            storymeta['title'] = thistitle
            storymeta['authgender'] = auth2gender[a]
            storymeta['docid'] = s
            auth_dates.append(storymeta['pubdate'])

            storyout.append(storymeta)

        # now lets calculate the average values for the author

        if len(auth_dates) < 1:
            continue

        authmeta = dict()
        authmeta['prob_mean'] = np.nanmean(auth_prob_means)  # we drop nans
        authmeta['prob_stdev'] = np.nanmean(auth_prob_stdev)  # for all these
        authmeta['prob_diff'] = np.nanmean(auth_prob_diffs)
        authmeta['weighted_diff'] = np.nanmean(auth_weighted_diffs)
        authmeta['wordratio'] = np.nanmean(auth_wordratios)
        authmeta['pct_women'] = np.nanmean(auth_charratios)
        authmeta['charsize'] = np.nanmean(auth_charsize_means)
        authmeta['numchars'] = np.nanmean(auth_num_chars)
        authmeta['meandate'] = np.mean(auth_dates)
        authmeta['author'] = a
        authmeta['authgender'] = auth2gender[a]
        authmeta['mean_prestige'] = auth_prestige_means[a]
        authmeta['num_stories'] = len(auth_dates)
        authmeta['mean_sales'] = auth_sales_means[a]

        authorout.append(authmeta)

authorcolumns = ['author', 'num_stories', 'authgender', 'meandate', 'mean_prestige', 'mean_sales', 'numchars', 'charsize', 'pct_women', 'wordratio', 'prob_diff', 'weighted_diff', 'prob_stdev', 'prob_mean']

storycolumns = ['docid', 'author', 'title', 'authgender', 'pubdate', 'numchars', 'charsize', 'pct_women', 'wordratio','prob_diff', 'weighted_diff', 'prob_stdev', 'prob_mean']

outpath = os.path.join(outdir, 'storymeta.tsv')
with open(outpath, mode = 'w', encoding = 'utf-8') as f:
    writer = csv.DictWriter(f, delimiter = '\t', fieldnames = storycolumns)
    writer.writeheader()
    for s in storyout:
        writer.writerow(s)

outpath = os.path.join(outdir, 'authormeta.tsv')
with open(outpath, mode = 'w', encoding = 'utf-8') as f:
    writer = csv.DictWriter(f, delimiter = '\t', fieldnames = authorcolumns)
    writer.writeheader()
    for a in authorout:
        writer.writerow(a)













