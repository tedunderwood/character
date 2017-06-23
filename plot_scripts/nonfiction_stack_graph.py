#!/usr/bin/env python3

# nonfiction_stack_graph.py

# Our goal here is to calculate what percentage of the books in each year
# that have known genders are either fiction by women, or other genres
# by women. Books by men are not going to be represented in the final
# stacked area graph, except as negative space.

import sys, csv, math
import numpy as np
import pandas as pd
from collections import Counter

allbooks = dict()
for i in range(1800, 2008):
    allbooks[i] = Counter()

# We're going to create three categories: fiction, other genres, and
# things by men.

with open('../metadata/filtered_fiction_metadata.csv', encoding = 'utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        docid=row[0]
        date=int(row[5])
        authgender=row[7]
        author=row[3]
        title=row[9]
        enumcron=row[8]

        if authgender == 'f':
            allbooks[date]['fiction'] += 1
        elif authgender == 'm':
            allbooks[date]['male'] += 1
        else:
            # note that gender 'u' is not counted
            pass

dateerrors = 0

with open('../nonfiction/nonfiction_genders.tsv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f, delimiter = '\t')
    for row in reader:
        try:
            date = int(row['date'])
        except:
            dateerrors += 1

        if date < 1800 or date > 2007:
            continue

        if row['Gender'] == 'F':
            allbooks[date]['other'] += 1
        elif row['Gender'] == 'M':
            allbooks[date]['male'] += 1
        else:
            # note that gender 'u' is not counted
            pass

# there are two nested loops here because we need
# to put the data in "long" format for ggplot
# visualization; the two genres will be represented
# successively instead of in two columns

with open('../dataforR/nonfiction_stack_graph.csv', mode = 'w', encoding = 'utf-8') as f:
    scribe = csv.DictWriter(f, fieldnames = ['year', 'genre', 'fraction'])
    scribe.writeheader()
    for genre in ['other', 'fiction']:
        for i in range(1800, 2008):
            totalforyear = allbooks[i]['male'] + allbooks[i]['femfiction'] + allbooks[i]['femother']
            thisratio = allbooks[i][genre] / totalforyear
            row = dict()
            row['year'] = i
            row['genre'] = genre
            row['fraction'] = thisratio
            scribe.writerow(row)

print('There were ' + str(dateerrors) + ' noninteger dates.')
# there are 0 errors in practice
