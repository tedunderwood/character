# combine_all_summaries

# this fuses the summary files from pre23_hathi,
# post22_hathi, and chicago, to create a file
# where there is only one entry for each
# char, auth, date tuple

import csv
from collections import Counter

counts = dict()

columns = ['characters', 'speaking', 'agent', 'mod', 'patient', 'poss', 'total']
fieldnames = ['chargender', 'authgender', 'date', 'characters', 'speaking', 'agent', 'mod', 'patient', 'poss', 'total']
def add2counts(filepath, counts):
    with open(filepath, encoding = 'utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            triplet = (row['chargender'], row['authgender'], row['date'])
            if triplet not in counts:
                counts[triplet] = Counter()
            for col in columns:
                counts[triplet][col] += int(row[col])

    return counts

add2counts('post22hathi/corrected_post22_summary.csv', counts)
add2counts('pre23hathi/corrected_pre23_hathi_summary.csv', counts)

with open('corrected_hathi_summaries.csv', mode = 'w', encoding = 'utf-8') as f:
    writer = csv.DictWriter(f, fieldnames = fieldnames)
    writer.writeheader()
    for triplet, colcounts in counts.items():
        r = dict()
        r['chargender'], r['authgender'], r['date'] = triplet
        for col in columns:
            r[col] = colcounts[col]
        writer.writerow(r)
