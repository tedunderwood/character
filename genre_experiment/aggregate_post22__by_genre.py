# aggregate_by_authgender.py

import json, csv, os, sys

from collections import Counter

# import utils
currentdir = os.path.dirname(__file__)
libpath = os.path.join(currentdir, '../../lib')
sys.path.append(libpath)

import SonicScrewdriver as utils

volgender = dict()
voldate = dict()
volbirth = dict()
volgenre = dict()

with open('../post22hathi/post22_corrected_metadata.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        volgender[row['docid']] = row['authgender']
        voldate[row['docid']] = int(row['inferreddate'])
        volbirth[row['docid']] = int(row['birthdate'])

with open('genredict.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        volgenre[row['docid']] = row['genre']

# Aggregate novels by year.

# characters are going to be divided both by character gender
# and by author gender, and each of those divisions
# will count up characters of a particular gender (or words spoken
# by those characters) for a particular date.


# words is further subdivided by the grammatical role of the word,
# plus a "total" category that aggregates counts for all four roles.

allgenders = ['u', 'f', 'm']

characters = dict()
words = dict()

genres = ['none', 'genre', 'romance']

# of these categories will be divided by (chargender, authgender)

for g1 in allgenders:
    for g2 in allgenders:
        words[(g1, g2)] = dict()
        for genre in genres:
            words[(g1, g2)][genre] = Counter()

print()
print('Aggregating results by year and genre.')

# Print results while aggregating for the next level.

skipped = 0
errors = 0

with open('../post22hathi/post22_character_data.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        docid = row['docid']

        if docid in voldate:
            date = voldate[docid]
        else:
            date = int(row['date'])

        if docid in volgender:
            authgender = volgender[docid]
        else:
            authgender = 'u'


        if docid in volgenre:
            genre = volgenre[docid]
        else:
            genre = 'none'
            errors += 1

        role = row['role']
        count = int(row['count'])
        chargender = row['gender']

        if role == 'speaking' or role == 'characters':
            continue
        else:
            words[(chargender, authgender)][genre][date] += count


fields = ['chargender', 'authgender', 'date', 'genre', 'total']
with open('post22_by_genre.csv', mode = 'w', encoding = 'utf-8') as f:
    writer = csv.DictWriter(f, fieldnames = fields)
    writer.writeheader()

    for chargender in allgenders:
        for authgender in allgenders:
            for g in genres:
                for date in range(1922, 2015):
                    outrow = dict()
                    outrow['chargender'] = chargender
                    outrow['authgender'] = authgender
                    outrow['date'] = date
                    outrow['genre'] = g
                    outrow['total'] = words[(chargender, authgender)][g][date]
                    writer.writerow(outrow)

print(skipped)
