#!/usr/bin/env python3

# pubweekly_gender_plots.py

# Python code to generate a new plot that integrates
# HathiTrust data with the PubWeekly sample. But I'm trying as far as possible to
# reuse David's code and work from the same source files so
# that we are guaranteed to be consistent.

# Python 3, however, which is one reason I made it a separate script.

# usage: python gender_plots.py fig1_ci post22_character_data.csv pre23_character_data.csv

# Note usage difference that this assumes the location of metadata in the
# metadata subn

import sys, csv, math
import numpy as np
import pandas as pd

metadata={}
seen = {}
docIdsByYear={}
knownAuthorsByYear={}
docIdsByYearWithKnownAuthor={}
seenDocs={}

roledict={"agent": 0, "patient": 1, "mod": 2, "poss": 3, "speaking": 4, "characters": 5}
data={}
genderdict={"f": 0, "m": 1}


def readmeta(filename):
    seen={}
    with open(filename, encoding = 'utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            docid=row[0]
            date=int(row[5])
            authgender=row[7]
            author=row[3]
            title=row[9]
            enumcron=row[8]

            if date not in knownAuthorsByYear:
                knownAuthorsByYear[date]=[]

            if authgender != "u" and docid not in seen:
                knownAuthorsByYear[date].append(docid)
                seen[docid]=1


            metadata[docid]=(date, authgender, title, author)

def read(filenames):
    for filename in filenames:
        with open(filename, encoding = 'utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                docid=row[0]
                date=int(row[1])
                gender=row[2]
                role=row[3]
                count=int(row[4])

                authgender='u'
                if docid in metadata:
                    (date, authgender, title, author)=metadata[docid]

                if date not in docIdsByYear:
                    docIdsByYear[date]=[]
                    docIdsByYearWithKnownAuthor[date]=[]

                # skip if character gender is unknown
                if gender == "u":
                    continue

                if docid not in seenDocs:
                    seenDocs[docid]=1
                    docIdsByYear[date].append(docid)

                    if authgender != 'u':
                        docIdsByYearWithKnownAuthor[date].append(docid)

                if docid not in data:
                    data[docid]=np.zeros((2,6))

                # multivolume works appear as multiple books with the same docid, so append counts rather than assign
                data[docid][genderdict[gender],roledict[role]]+=count

def writeauthorratios():

    authgenderratios = {}
    for year in range(1800,2008):
        counts=np.zeros(2)
        for docid in knownAuthorsByYear[year]:
            (date, authorgender, title, author)=metadata[docid]
            counts[genderdict[authorgender]]+=1

        authgenderratios[year] = (counts[0]/np.sum(counts))

    with open('../dataforR/authorratios.csv', mode = 'w', encoding = 'utf-8') as f:
        f.write('year,authratio\n')
        for year in range(1800, 2008):
            f.write(str(year) + ',' + str(authgenderratios[year]) + '\n')

    # Not ideal to write out intermediate data, but I'm going to do the final
    # plotting in R.

def writePWerrorbars():
    dates = [1890, 1920, 1955, 1985]
    pubweekly = pd.read_csv('../pubweekly/masterpubweeklydata.csv')
    rows = []
    for d in dates:
        recordsforyear = pubweekly[pubweekly.date == d]
        means = []

        # I'm doing this in a complex way, because the actual gender values can
        # be m, f, or u, and I suspect the u (unknown) values are not irrelevant
        # to the bootstrap resampling, even though I want to calculate only
        # f / (m + f)

        for i in range(1000):
            thissample = np.random.choice(recordsforyear.gender, len(recordsforyear.gender))
            women = 0
            knowngenders = 0
            for g in thissample:
                if g == 'f':
                    women += 1
                    knowngenders += 1
                elif g == 'm':
                    knowngenders += 1

            thismean = women / knowngenders
            means.append(thismean)
        lowmiddlehigh = np.percentile(means, [2.5, 50, 97.5])
        row = dict()
        row['year'] = d
        row['low'] = lowmiddlehigh[0]
        row['mean'] = lowmiddlehigh[1]
        row['high'] = lowmiddlehigh[2]
        rows.append(row)

    with open('../dataforR/pubweeklyerrorbars.csv', mode = 'w', encoding = 'utf-8') as f:
        scribe = csv.DictWriter(f, fieldnames = ['year', 'low', 'mean', 'high'])
        scribe.writeheader()
        for row in rows:
            scribe.writerow(row)


chart=sys.argv[1]
readmeta('../metadata/filtered_fiction_metadata.csv')

# this is in the repo file structure, so should/could be in the same position
# relative to this script on each of our computers

read(['../post22hathi/post22_character_data.csv', '../pre23hathi/pre23_character_data.csv'])

if chart == 'authorratios':
    writeauthorratios()
if chart == 'PWerrorbars':
    writePWerrorbars()
