import csv, os, sys
import pandas as pd
import numpy as np

from collections import Counter

# import utils
currentdir = os.path.dirname(__file__)
libpath = os.path.join(currentdir, '../../lib')
sys.path.append(libpath)

import SonicScrewdriver as utils

prestige = pd.read_csv('/Users/tunder/Dropbox/GenreProject/python/reception/fiction/prestigery.csv')
metadata = pd.read_csv('/Users/tunder/Dropbox/python/character/metadata/filtered_fiction_plus_18c.tsv', sep ='\t')

metadata['volid'] = metadata.volid.apply(utils.clean_pairtree)

# Let's start by identifying all stories in our metadata by
# authors in the prestige dataset. We're only going to consider
# the first 25 chars of authname

def trim_to_25(aname):
    if type(aname) != str:
        return 'Anonymous'

    aname = aname.strip('(),. .{0123456789]').lower()
    if len (aname) > 24:
        return aname[0:24]
    else:
        return aname

known_authors = set([trim_to_25(a) for a in prestige.author])
prestige['trimmedauth'] = prestige.author.apply(trim_to_25)
metadata['trimmedauth'] = metadata.author.apply(trim_to_25)
all_matches = set(metadata.trimmedauth)

auth2story = dict()
auth2gender = dict()
auth_prestige_means = dict()

for a in known_authors:
    if a in all_matches:
        stories = metadata.loc[metadata.trimmedauth == a, 'docid']
        auth2story[a] = list(stories)
        authgender = metadata.loc[metadata.trimmedauth == a, 'authgender']
        if len(authgender) > 0:
            authgender = authgender.iloc[0]
            auth2gender[a] = authgender

    vol_predictions = prestige.loc[prestige.trimmedauth == a, 'logistic']
    auth_prestige_means[a] = np.mean(vol_predictions)


# now let's get all the characters for each story

data = pd.read_csv('/Users/tunder/Dropbox/python/character/data/character_probabilities.tsv', sep = '\t')
#loads characters

storydates = dict()
authorout = []
storyout = []

for a in known_authors:
    auth_prob_means = []
    auth_prob_diffs = []
    auth_charratios = []
    auth_wordratios = []
    auth_prob_stdev = []
    auth_charsize_means = []
    auth_num_chars = []
    auth_dates = []

    if a in auth2story:
        stories = auth2story[a]

        for s in stories:
            story_probs = dict()
            undifferentiated_probs = []
            story_genders = Counter()
            story_words = Counter()
            charsizes = []
            storymeta = dict()    # initialize the output record

            chars = data.loc[data.docid == s, : ]
            for i in chars.index:
                num_words = int(chars.loc[i, 'numwords'])
                if num_words < 15:
                    continue
                else:
                    charsizes.append(num_words)

                prob_feminine = chars.loc[i, 'probability']
                actual_gender = chars.loc[i, 'gender']
                storymeta['pubdate'] = chars.loc[i, 'pubdate']
                # that will happen redundantly, but wth

                story_words[actual_gender] += num_words
                story_genders[actual_gender] += 1
                if actual_gender not in story_probs:
                    story_probs[actual_gender] = []
                story_probs[actual_gender].append(prob_feminine)
                undifferentiated_probs.append(prob_feminine)

            # now compute summary statistics for all characters
            # unless there were none!

            if len(chars.index) < 1 or 'pubdate' not in storymeta:
                continue

            prob_mean = np.mean(undifferentiated_probs)

            if story_genders['f'] > 0 and story_genders['m'] > 0:
                prob_diff = np.mean(story_probs['f']) - np.mean(story_probs['m'])
            else:
                prob_diff = float('nan')

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
            storymeta['wordratio'] = wordratio
            auth_wordratios.append(wordratio)
            storymeta['pct_women'] = charratio
            auth_charratios.append(charratio)
            storymeta['charsize'] = charsize_mean
            auth_charsize_means.append(charsize_mean)
            storymeta['numchars'] = len(charsizes)
            auth_num_chars.append(len(charsizes))
            storymeta['author'] = a
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
        authmeta['wordratio'] = np.nanmean(auth_wordratios)
        authmeta['pct_women'] = np.nanmean(auth_charratios)
        authmeta['charsize'] = np.nanmean(auth_charsize_means)
        authmeta['numchars'] = np.nanmean(auth_num_chars)
        authmeta['meandate'] = np.mean(auth_dates)
        authmeta['author'] = a
        authmeta['authgender'] = auth2gender[a]
        authmeta['mean_prestige'] = auth_prestige_means[a]
        authmeta['num_stories'] = len(auth_dates)

        authorout.append(authmeta)

authorcolumns = ['author', 'num_stories', 'authgender', 'meandate', 'mean_prestige', 'numchars', 'charsize', 'pct_women', 'wordratio', 'prob_diff', 'prob_stdev', 'prob_mean']

storycolumns = ['docid', 'author', 'authgender', 'pubdate', 'numchars', 'charsize', 'pct_women', 'wordratio','prob_diff', 'prob_stdev', 'prob_mean']

with open('storymeta.tsv', mode = 'w', encoding = 'utf-8') as f:
    writer = csv.DictWriter(f, delimiter = '\t', fieldnames = storycolumns)
    writer.writeheader()
    for s in storyout:
        writer.writerow(s)

with open('authormeta.tsv', mode = 'w', encoding = 'utf-8') as f:
    writer = csv.DictWriter(f, delimiter = '\t', fieldnames = authorcolumns)
    writer.writeheader()
    for a in authorout:
        writer.writerow(a)













