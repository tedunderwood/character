#!/usr/bin/env python3

# transform_decade_grid

import csv

maximums = dict()
L2s = dict()

with open('../dataforR/decadegrid.tsv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f, delimiter = '\t')
    for row in reader:
        key = (row['decade'], row['iter'])
        accuracy = float(row['accuracy'])
        if key not in maximums:
            maximums[key] = accuracy
            L2s[key] = row['L2']
        elif maximums[key] < accuracy:
            maximums[key] = accuracy
            L2s[key] = row['L2']


with open('../dataforR/decade_optimums.tsv', mode = 'w', encoding = 'utf-8') as f:
    f.write('decade\tL2\taccuracy\n')
    for key, acc in maximums.items():
        decade = key[0]
        L2 = L2s[key]
        f.write(decade + '\t' + L2 + '\t' + str(acc) + '\n')






