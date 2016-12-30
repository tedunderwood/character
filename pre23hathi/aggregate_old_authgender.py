# aggregate_by_authgender.py

import json, csv, os, sys

from collections import Counter

volgender = dict()
voldate = dict()
volbirth = dict()
mindate = 3000
maxdate = 0

with open('pre23_corrected_metadata.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        volgender[row['docid']] = row['authgender']
        date = int(row['inferreddate'])
        voldate[row['docid']] = date
        if date < mindate:
            mindate = date
        if date > maxdate:
            maxdate = date

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
speech = dict()

rolesplustotal = ['agent', 'mod', 'patient', 'poss', 'total']

# of these categories will be divided by (chargender, authgender)

for g1 in allgenders:
    for g2 in allgenders:
        characters[(g1, g2)] = Counter()
        speech[(g1, g2)] = Counter()
        words[(g1, g2)] = dict()
        for role in rolesplustotal:
            words[(g1, g2)][role] = Counter()

print()
print('Aggregating results by year.')

# Print results while aggregating for the next level.

skipped = 0
errors = 0

with open('pre23_character_data.csv', encoding = 'utf-8') as f:
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
            errors += 1

        role = row['role']
        count = int(row['count'])
        chargender = row['gender']

        if role == 'speaking':
            speech[(chargender, authgender)][date] += count
        elif role == 'characters':
            characters[(chargender, authgender)][date] += count
        else:
            words[(chargender, authgender)][role][date] += count
            words[(chargender, authgender)]['total'][date] += count
            # Each category also gets added to the 'total' category.


fields = ['chargender', 'authgender', 'date', 'characters', 'speaking', 'agent', 'mod', 'patient', 'poss', 'total']
with open('corrected_pre23_hathi_summary.csv', mode = 'w', encoding = 'utf-8') as f:
    writer = csv.DictWriter(f, fieldnames = fields)
    writer.writeheader()

    for chargender in allgenders:
        for authgender in allgenders:
            for date in range(mindate, (maxdate + 1)):
                outrow = dict()
                outrow['chargender'] = chargender
                outrow['authgender'] = authgender
                outrow['date'] = date
                outrow['characters'] = characters[(chargender, authgender)][date]
                outrow['speaking'] = speech[(chargender, authgender)][date]
                for role in rolesplustotal:
                    outrow[role] = words[(chargender, authgender)][role][date]
                writer.writerow(outrow)

print(skipped)
