#!/usr/bin/env python3

# genre_namematcher

# this version of namematcher is a little more generous
# a) because the genre dataset is better groomed than
#    pairedwithprestige, and
# b) because we're going to be matching at the volume level
#    and using titles as an additional measure of certainty

# so instead of tossing a match if it has even one word that can't be
# paired with an initial, we allow one extra name

import csv, os, sys
import pandas as pd

prestige = pd.read_csv('rawgenredata.csv')
goodset = set(prestige.author)

metadata = pd.read_csv('../metadata/filtered_fiction_plus_18c.tsv', sep ='\t')
badset = set(metadata.author)

trans_table = str.maketrans('.,()[]{}', '        ')

def getinitials(listofwords):
    initials = set()
    for l in listofwords:
        if len(l) == 1:
            initials.add(l)
    return initials

def getnamestarts(listofwords):
    starts = set()
    for l in listofwords:
        if len(l) > 1:
            starts.add(l[0])
    return starts


def checkmatch(a, b):

    honorifics = {'Lord', 'Lady', 'Mrs', 'Mr', 'Miss', 'Sir', 'Hon', 'Baron', 'Baroness'}
    global trans_table

    awords = set(a.translate(trans_table).split())
    bwords = set(b.translate(trans_table).split())

    awords = awords - honorifics
    bwords = bwords - honorifics

    ainitials = getinitials(awords)
    binitials = getinitials(bwords)

    astarts = getnamestarts(awords)
    bstarts = getnamestarts(bwords)

    unmatched = 0

    for w in awords - bwords:
        if len(w) > 1 and w[0] in binitials:
            continue
        elif len(w) == 1 and w in bstarts:
            continue
        else:
            unmatched += 1

    for w in bwords - awords:
        if len(w) > 1 and w[0] in ainitials:
            continue
        elif len(w) == 1 and w in astarts:
            continue
        else:
            unmatched += 1

    return unmatched

allmatches = []
allfails = []

for a in goodset:

    if type(a) == float:
        continue

    if len(a) > 14:
        asegment = a[0:14]
    else:
        asegment = a

    for b in badset:
        if a == b:
            continue
        elif type(b) != str:
            continue
        elif b.strip(',') == a:
            continue

        elif asegment in b:
            unmatch = checkmatch(a, b)
            if unmatch < 2:
                allmatches.append((b, a))
            elif unmatch == 2:
                allfails.append((b, a))

with open('genres_in_filteredfic.tsv', mode = 'w', encoding = 'utf-8') as f:
    f.write('alias\tourname\n')
    for alias, name in allmatches:
        f.write(alias + '\t' + name + '\n')

with open('near_genres_in_filteredfic.tsv', mode = 'w', encoding = 'utf-8') as f:
    f.write('alias\tourname\n')
    for alias, name in allfails:
        f.write(alias + '\t' + name + '\n')



