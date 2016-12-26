import glob, os, sys, csv
from collections import Counter

datedict = dict()

with open('/Volumes/TARDIS/US_Novel_Corpus/metadata/NOVELS_METADATA.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        docid = row['BOOK_ID']
        missing = 8 - len(docid)
        docid = ('0' * missing) + docid
        date = int(row['PUBL_DATE'])
        datedict[docid] = date

wordsaboutwomen = Counter()
wordsaboutmen = Counter()
roles2count = {'agent', 'mod', 'patient', 'poss'}

yraboutwomen = Counter()
yraboutmen = Counter()

with open('/Users/tunder/Dropbox/python/character/chicago/chicago_character_data.csv', encoding = 'utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        docid = row['docid']
        if docid not in datedict:
            print("Dateless " + docid)
            continue
        else:
            date = datedict[docid]

        if row['role'] not in roles2count:
            continue

        if row['gender'] == 'm':
            wordsaboutmen[docid] += int(row['count'])
            yraboutmen[date] += int(row['count'])
        elif row['gender'] == 'f':
            wordsaboutwomen[docid] += int(row['count'])
            yraboutwomen[date] += int(row['count'])

wordratio = dict()
yrwordratio = dict()

for docid, womanct in wordsaboutwomen.items():
    wordratio[docid] = womanct / (womanct + wordsaboutmen[docid] + 0.001)

for date, womanct in yraboutwomen.items():
    yrwordratio[date] = womanct / (womanct + yraboutmen[date] + 0.001)

filepaths = glob.glob('/Volumes/TARDIS/US_Novel_Corpus/NOVELS_1880-1990/*.txt')

hehim = {'he', 'him' 'his', 'himself'}
sheher = {'she', 'her', 'hers', 'herself'}

heshe = dict()
heyear = Counter()
sheyear = Counter()

for path in filepaths:
    docid = path.split('/')[-1].replace('.txt', '')
    if docid not in wordratio:
        print(docid)
        continue
    date = datedict[docid]

    with open(path, encoding = 'utf-8') as f:
        lines = f.readlines()
    hectr = 0
    shectr = 0
    for line in lines:
        line = line.replace('.', ' ')
        line = line.replace(',', ' ')
        line = line.replace('"', ' ')
        words = line.lower().split()
        for w in words:

            if w in hehim:
                hectr += 1
                heyear[date] += 1
            elif w in sheher:
                shectr += 1
                sheyear[date] += 1

    if (hectr + shectr) > 0:
        heshe[docid] = shectr / (hectr + shectr)

with open('chicagocheck.csv', mode = 'w', encoding = 'utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['docid', 'heshe', 'wordratio'])
    for docid, hs in heshe.items():
        if docid in wordratio:
            writer.writerow([docid, hs, wordratio[docid]])

yrheshe = dict()
for date, shect in sheyear.items():
    if shect > 0 and date in heyear:
        yrheshe[date] = shect / (shect + heyear[date])

with open('chicagoyrcheck.csv', mode = 'w', encoding = 'utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['year', 'pronratio', 'wordratio'])
    for date, pratio in yrheshe.items():
        if date in yrwordratio:
            writer.writerow([date, pratio, yrwordratio[date]])









