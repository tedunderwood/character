# This script reflect some adhoc cleaning I did
# to remove juvenile fiction and biography that
# had crept into the 1900-22 segment of the timeline,
# because that segment was modeled separately

import json, csv, os, sys

from collections import Counter

# import utils
currentdir = os.path.dirname(__file__)
libpath = os.path.join(currentdir, '../lib')
sys.path.append(libpath)

import SonicScrewdriver as utils

docstoget = set()
docgenders = dict()

with open('/Users/tunder/Dropbox/python/character/metadata/filtered_fiction_metadata.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = int(row['inferreddate'])
        if date > 1899 and date < 1923:
            docstoget.add(row['volid'])
            docgenders[row['volid']] = row['authgender']

juvie = []
nonjuv = set()
jrows = []

with open('/Volumes/TARDIS/work/metadata/20cMonographMetadata.tsv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f, delimiter = '\t')
    oldfields = reader.fieldnames
    for row in reader:
        docid = utils.clean_pairtree(row['HTid'])
        if docid in docstoget:
            subjects = row['subjects'].lower()
            genres = row['genres'].lower()
            if 'biography' in genres:
                juvie.append(docid)
                jrows.append(row)
            elif 'children' in subjects or 'children' in genres:
                juvie.append(docid)
                jrows.append(row)
            elif 'biography' in subjects or 'biography' in genres:
                juvie.append(docid)
                jrows.append(row)
            elif 'juvenile' in subjects or 'juvenile' in genres:
                juvie.append(docid)
                jrows.append(row)
            else:
                nonjuv.add(docid)

tokeep = []

with open('/Users/tunder/Dropbox/python/character/metadata/filtered_fiction_metadata.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        date = int(row['inferreddate'])
        if date > 1899 and date < 1923:
            docid = row['volid']
            if docid in nonjuv:
                tokeep.append(row)
        else:
            tokeep.append(row)

with open('/Users/tunder/Dropbox/python/character/metadata/filtered_fiction_metadata2.csv', mode = 'w', encoding = 'utf-8') as f:
    scribe = csv.DictWriter(f, fieldnames = fieldnames)
    scribe.writeheader()
    for row in tokeep:
        scribe.writerow(row)

with open('/Users/tunder/Dropbox/python/character/metadata/discarded19001922.csv', mode = 'w', encoding = 'utf-8') as f:
    scribe = csv.DictWriter(f, fieldnames = oldfields)
    scribe.writeheader()
    for row in jrows:
        scribe.writerow(row)





