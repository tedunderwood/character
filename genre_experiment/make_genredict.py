# make_genredict.py

import csv, os, sys

# import utils
currentdir = os.path.dirname(__file__)
libpath = os.path.join(currentdir, '../../lib')
sys.path.append(libpath)

import SonicScrewdriver as utils

docs2categorize = set()

with open('../post22hathi/post22_character_data.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        docid = row['docid']
        docs2categorize.add(docid)

with open('../pre23hathi/pre23_character_data.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        docid = row['docid']
        docs2categorize.add(docid)

tocheck = ['/Volumes/TARDIS/work/fullmeta/newmeta/new_pd_google_1.tsv', '/Volumes/TARDIS/work/fullmeta/newmeta/new_pd_google_2.tsv', '/Volumes/TARDIS/work/fullmeta/newmeta/new_pd_google_3.tsv', '/Volumes/TARDIS/work/fullmeta/newmeta/new_oa.tsv', '/Volumes/TARDIS/work/fullmeta/newmeta/new_restricted.tsv',
    '/Volumes/TARDIS/work/fullmeta/ic_monographs.tsv']

genrecats = ['suspense', 'adventure', 'western', 'mystery', 'detective', 'science fiction', 'fantasy', 'horror', 'gothic', 'romance', 'pulp']

doublets = []

for afile in tocheck:
    with open(afile, encoding = 'utf-8') as f:
        reader = csv.DictReader(f, delimiter = '\t', quoting = csv.QUOTE_NONE)
        for row in reader:
            docid = row['docid']
            alternative = utils.clean_pairtree(docid)
            if docid in docs2categorize:
                dothis = True
                d = docid
            elif alternative in docs2categorize:
                dothis = True
                d = alternative
            else:
                dothis = False

            if dothis:
                g = row['genres'].lower() + " " + row['subjects'].lower()
                genre = 'none'
                for cat in genrecats:
                    if cat in g:
                        genre = 'genre'
                        break
                doublets.append((d, genre))

with open('genredict.csv', mode = 'w', encoding = 'utf-8') as f:
    f.write('docid,genre\n')
    for d, g in doublets:
        f.write(d + ',' + g + '\n')






