#!/usr/bin/env python3

# gather_genre_data.py

# gathers genre records from a number of
# locations, and assembles them in a
# minimal form

import csv, os, sys
import pandas as pd

detectivetags = {'det100', 'locdetective', 'locdetmyst', 'chimyst', 'crime'}
sftags = {'femscifi', 'chiscifi', 'anatscifi', 'locscifi'}

gathered = dict()
gathered['author'] = []
gathered['title'] = []
gathered['volid'] = []
gathered['pubdate'] = []
gathered['authgender'] = []
gathered['genre'] = []

with open('/Users/tunder/Dropbox/python/character/bestsellergender/20thcRomances.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        gathered['author'].append(row['PublishingName'])
        gathered['title'].append(row['Title'])
        gathered['pubdate'].append(int(row['Date']))
        gathered['volid'].append(row['HathiID'])
        gathered['authgender'].append('f')
        gathered['genre'].append('romance')

with open('/Users/tunder/Dropbox/python/character/bestsellergender/19thcRomances.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        gathered['author'].append(row['PublishingName'])
        gathered['title'].append(row['Title'])
        gathered['pubdate'].append(int(row['Date']))
        gathered['volid'].append(row['HathiID'])
        gathered['authgender'].append('u')
        gathered['genre'].append('romance')

with open('/Users/tunder/Dropbox/fiction/meta/concatenatedmeta.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        genres = set([x.strip() for x in row['genretags'].split('|')])

        if len(genres.intersection(sftags)) > 0:
            thisgenre = 'scifi'
        elif len(genres.intersection(detectivetags)) > 0:
            thisgenre = 'detective'
        else:
            continue

        gathered['volid'].append(row['docid'])
        gathered['author'].append(row['author'])
        gathered['title'].append(row['title'])
        gathered['pubdate'].append(row['firstpub'])
        gathered['genre'].append(thisgenre)
        if len(row['gender']) < 1:
            gender = 'u'
        else:
            gender = row['gender']
        gathered['authgender'].append(gender)

df = pd.DataFrame(gathered)
df.to_csv('rawgenredata.csv')



