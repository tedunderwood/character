#!/usr/bin/env python3

# restore_18c.py

# In creating filtered_fiction_metadata,
# I cut everything before 1800. But for modeling,
# it's worth stretching back to 1780
# So let's add back those 20 years.

import csv

rowlist = []

with open('/Users/tunder/Dropbox/character/meta/charmeta.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        n = dict()
        n['docid'] = row['storyID']
        n['inferreddate'] = int(row['date'])
        if n['inferreddate'] < 1780 or n['inferreddate'] > 1799:
            continue
        n['volid'] = row['htid']
        n['recordid'] = ''
        n['author'] = row['author']
        n['title'] = row['title']
        n['firstname'] = ''
        if ',' in row['author']:
            n['firstname'] = row['author'].split(',')[1].strip(',.')
        n['birthdate'] = ''
        n['authgender']= row['authgender']
        n['enumcron'] = row['enumcron']
        rowlist.append(n)

with open('../metadata/filtered_fiction_metadata.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        rowlist.append(row)

with open('../metadata/filtered_fiction_plus_18c.tsv', mode = 'w', encoding = 'utf-8') as f:
    scribe = csv.DictWriter(f, delimiter = '\t', fieldnames = fieldnames)
    scribe.writeheader()
    for row in rowlist:
        scribe.writerow(row)
