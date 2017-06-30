#!/usr/bin/env python3

# select_balanced_subset.py

# Selects a subset of characters from each decade to be
# used for modeling. The tricky aspect of this is, you
# want
#
# 1) an equal number of characters in each decade,
#
# 2) an equal number of characters with masculine names
# and feminine names in each decade
#
# 3) finally, you want all of these groups to be described
# with roughly the same number of words in each decade, lest
# larger characters create stronger models,

import numpy as np
import math, csv, random, sys, os
from collections import Counter

csv.field_size_limit(sys.maxsize)
# cause some of those fields are long

mediantarget = 54
# target median num of words for characters

TARGET = 2000
# target number of characters per gender per decade

forbidden = {'he', 'she', 'her', 'him', 'manhood', 'womanhood', 'boyhood', 'girlhood', 'husband', 'wife', 'lordship', 'ladyship', 'man', 'woman', 'mistress', 'daughter', 'son', 'girl', 'boy', 'bride', 'fiancé', 'fiancée', 'brother', 'sister', 'lady', 'gentleman'}

allmeta = dict()

with open('../metadata/filtered_fiction_plus_18c.tsv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f, delimiter = '\t')
    for row in reader:
        story = row['docid']
        allmeta[story] = row

def cossim(v1, v2):
    return np.dot(v1, v2) / (np.sqrt(np.dot(v1, v1)) * np.sqrt(np.dot(v2, v2)))

def addgroup(groupofchars, allmeta, allrows, genderflag):

    for char in groupofchars:
        this = dict()
        nameparts = char.split('|')
        storyid = nameparts[0]
        metarow = allmeta[storyid]

        this['docid'] = char
        this['date'] = metarow['inferreddate']
        this['firstpub'] = metarow['inferreddate']
        this['authgender'] = metarow['authgender']
        this['nationality'] = ''
        this['gender'] = genderflag
        this['tags'] = genderflag
        this['birthdate'] = 0
        this['author'] = metarow['author']
        if this['author'] == '<blank>':
            this['author'] = 'anon' + storyid
        this['title'] = metarow['title']
        this['storyid'] = storyid

        allrows.append(this)

def select_from_source(sourcepath, startdate, enddate):
    '''
    Selects an even number of male and female characters
    trying to get #TARGET men and #TARGET women in each decade.
    Writes metadata and data.
    '''

    global allmeta, mediantarget, TARGET, forbidden

    malecharacters = dict()
    femalecharacters = dict()

    with open(sourcepath, encoding = "utf-8") as f:
        reader = csv.DictReader(f, delimiter = '\t', quoting = csv.QUOTE_NONE)
        for row in reader:
            thischar = row['charid']
            gender = row['gender']
            date = int(row['pubdate'])
            words = row['words'].split(' ')
            docsize = len(words)
            if docsize < 16:
                continue
            # we're ignoring minor characters
            else:
                # let's only count words that can be used
                docsize = 0
                for word in words:
                    if word not in forbidden and not word.startswith('said-'):
                        docsize += 1

            if docsize < 16:
                continue

            charname = row['charname']

            if charname == "I" or charname == "" or date < 1780 or date > 2009:
                continue
                # We're not going to use characters of unknown gender, or first-
                # person chars (because we don't know gender), or characters
                # outside our date range
            elif gender.startswith('m'):
                if date not in malecharacters:
                    malecharacters[date] = dict()
                malecharacters[date][thischar] = docsize
            elif gender.startswith('f'):
                if date not in femalecharacters:
                    femalecharacters[date] = dict()
                femalecharacters[date][thischar] = docsize

    allrows = []

    for floor in range(startdate, enddate, 10):
        ceiling = floor + 10
        if floor == 1780:
            ceiling = floor + 20
        elif floor == 1790:
            continue

        print(floor)
        malecount = 0
        malecandidates = []

        for i in range(floor, ceiling):
            if i in malecharacters:
                for character, size in malecharacters[i].items():
                    malecount += 1
                    malecandidates.append((size, character))

        femalecount = 0
        femalecandidates = []

        for i in range(floor, ceiling):
            if i in femalecharacters:
                for character, size in femalecharacters[i].items():
                    femalecount += 1
                    femalecandidates.append((size, character))

        leastnum = min(malecount, femalecount)
        if leastnum < TARGET:
            print('Resetting target to ' + str(leastnum))
            decade_target = leastnum
        else:
            decade_target = TARGET

        malegroup = random.sample(malecandidates, decade_target - 200)
        femalegroup = random.sample(femalecandidates, decade_target - 200)

        for m in malegroup:
            i = malecandidates.index(m)
            malecandidates.pop(i)

        for f in femalegroup:
            i = femalecandidates.index(f)
            femalecandidates.pop(i)

        malecandidates.sort()
        femalecandidates.sort()
        malegroup.sort()
        femalegroup.sort()

        for i in range(200):
            malegroup.sort()
            femalegroup.sort()
            malemedidx = len(malegroup) // 2
            femalemedidx = len(femalegroup) // 2
            malemedian, char = malegroup[malemedidx]
            femalemedian, char = femalegroup[femalemedidx]

            malecut = 0
            femalecut = 0
            malelen = len(malecandidates)
            femalelen = len(femalecandidates)

            for idx, m in enumerate(malecandidates):
                size, character = m
                if size > mediantarget:
                    malecut = idx
                    break

            for idx, f in enumerate(femalecandidates):
                size, character = f
                if size > mediantarget:
                    femalecut = idx
                    break

            if malecut == 0 or femalecut == 0:
                # we don't have options anymore
                print("No options: ", malecut, femalecut)
                break

            if malemedian - 2 > mediantarget:
                idx = 0
            elif malemedian > mediantarget:
                idx = random.sample([x for x in range(malecut)], 1)[0]
            elif malemedian + 2 < mediantarget:
                idx = malelen - 1
            else:
                idx = random.sample([x for x in range(malecut, malelen)], 1)[0]
            malegroup.append(malecandidates.pop(idx))

            if femalemedian - 2 > mediantarget:
                idx = 0
            elif femalemedian > mediantarget:
                idx = random.sample([x for x in range(femalecut)], 1)[0]
            elif femalemedian + 2 < mediantarget:
                idx = femalelen - 1
            else:
                idx = random.sample([x for x in range(femalecut, femalelen)], 1)[0]
            femalegroup.append(femalecandidates.pop(idx))
            print(malemedian,femalemedian)

        malechars = []
        malesizes = []
        for size, character in malegroup:
            malechars.append(character)
            malesizes.append(size)


        femalechars = []
        femalesizes = []
        for size, character in femalegroup:
            femalechars.append(character)
            femalesizes.append(size)

        print("male characters: " + str(len(malesizes)) + 'chars,  mean: ' + str(sum(malesizes) / len(malesizes)))
        print(malesizes[(len(malesizes) // 2)])
        print("female: " + str(len(femalesizes)) + ' chars, mean: ' +  str(sum(femalesizes) / len(femalesizes)))
        print(femalesizes[(len(malesizes) // 2)])
        print()

        addgroup(malechars, allmeta, allrows, 'm')
        addgroup(femalechars, allmeta, allrows, 'f')

    fields = ['docid', 'storyid', 'date', 'gender', 'author', 'title', 'authgender', 'nationality', 'firstpub', 'tags', 'birthdate']

    selectedchars = set()

    print('Writing metadata ...')

    metapath = '/Users/tunder/Dropbox/python/character/metadata/balanced_character_subset.csv'
    if not os.path.isfile(metapath):
        writeheader = True
    else:
        writeheader = False

    with open(metapath, mode = 'a', encoding = 'utf-8') as f:
        writer = csv.DictWriter(f, fieldnames = fields)
        if writeheader:
            writer.writeheader()
        for row in allrows:
            writer.writerow(row)
            selectedchars.add(row['docid'])

    targetdir = '/Users/tunder/data/character_subset/'

    outdata = dict()
    wordtotals = Counter()

    print('Getting words ...')

    with open(sourcepath, encoding = "utf-8") as f:
        reader = csv.DictReader(f, delimiter = '\t', quoting = csv.QUOTE_NONE)
        for row in reader:
            thischar = row['charid']

            if thischar not in selectedchars:
                continue


            words = row['words'].split(' ')

            if len(words) < 16:
                print('error 2')
                continue
            # we're ignoring minor characters

            outdata[thischar] = Counter()
            for word in words:
                if word not in forbidden and not word.startswith('said-'):
                    outdata[thischar][word] += 1
                    wordtotals[thischar] += 1

    print('Writing data ...')

    for charname, wordcounts in outdata.items():
        outpath = targetdir + charname + '.tsv'
        thistotal = wordtotals[charname]
        with open(outpath, mode = 'w', encoding = 'utf8') as f:
            for word, count in wordcounts.items():
                f.write(word + '\t' + str(count / thistotal) + '\n')


# MAIN

select_from_source("/Users/tunder/data/chartable18c19c.tsv", 1780, 1900)
select_from_source("/Users/tunder/data/chartablepost1900.tsv", 1900, 2010)









