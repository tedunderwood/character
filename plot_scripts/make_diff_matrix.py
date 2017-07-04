# Make diff matrix.

VOCABLENGTH = 6000

import csv, sys
import numpy as np
import pandas as pd
import math
# from random import shuffle
# from random import random as randomprob
from sklearn.linear_model import LinearRegression
from collections import Counter

csv.field_size_limit(sys.maxsize)

# Let's load some metadata about the publication dates of these works,
# and the inferred genders of their authors.

personalnames = set()
with open("/Users/tunder/Dropbox/booknlpscripts/PersonalNames.txt", encoding="utf-8") as f:
    names = f.readlines()

for line in names:
    name = line.rstrip()
    personalnames.add(name)
    personalnames.add('said-' + name)

vocab = Counter()

def add2vocab(vocab, filepath):
    with open(filepath, encoding = 'utf-8') as f:
        reader = csv.DictReader(f, delimiter = '\t')
        for row in reader:
            words = row['words'].split()
            for w in words:
                if not w.startswith('said-') and w not in personalnames:
                    vocab[w] += 1

add2vocab(vocab, '../data/chartable18c19c.tsv')
add2vocab(vocab, '../data/chartablepost1900.tsv')

vocabcount = len(vocab)
print("The data includes " + str(vocabcount) + " words")

wordsinorder = [x[0] for x in vocab.most_common(VOCABLENGTH)]

vocabulary = dict()
vocabset = set()

for idx, word in enumerate(wordsinorder):
    vocabulary[word] = idx
    vocabset.add(word)
print("Vocabulary sorted, top " + str(VOCABLENGTH) + " kept.")


vecbyyear = dict()
vecbyyear['m'] = dict()
vecbyyear['f'] = dict()
datevector = list(range(1780, 2008))

for g in ['f', 'm']:
    for i in range(1780, 2008):
        vecbyyear[g][i] = np.zeros((VOCABLENGTH))

def add2counts(vecbyyear, path):
    with open(path, encoding = 'utf-8') as f:
        reader = csv.DictReader(f, delimiter = '\t')
        for row in reader:
            gender = row['gender']

            if gender.startswith('u'):
                continue

            date = int(row['pubdate'])
            if date < 1780 or date > 2008:
                continue

            words = row['words'].split()
            for w in words:
                if w in vocabset:
                    idx = vocabulary[w]
                    np.add.at(vecbyyear[gender][date], idx, 1)

add2counts(vecbyyear, '../data/chartable18c19c.tsv')
add2counts(vecbyyear, '../data/chartablepost1900.tsv')

def dunnings(vectora, vectorb):
    assert len(vectora) == len(vectorb)
    veclen = len(vectora)
    totala = np.sum(vectora)
    totalb = np.sum(vectorb)
    totalboth = totala + totalb

    dunningvector = np.zeros(veclen)

    for i in range(veclen):
        if vectora[i] == 0 or vectorb[i] == 0:
            continue
            # Cause you know you're going to get div0 errors.

        try:
            probI = (vectora[i] + vectorb[i]) / totalboth
            probnotI = 1 - probI
            expectedIA = totala * probI
            expectedIB = totalb * probI
            expectedNotIA = totala * probnotI
            expectedNotIB = totalb * probnotI
            expected_table = np.array([[expectedIA, expectedNotIA],
                [expectedIB, expectedNotIB]])
            actual_table = np.array([[vectora[i], (totala - vectora[i])],
                [vectorb[i], (totalb - vectorb[i])]])
            G = np.sum(actual_table * np.log(actual_table / expected_table))

            # We're going to use a signed version of Dunnings, so features where
            # B is higher than expected will be negative.

            if expectedIB > vectorb[i]:
                G = -G

            dunningvector[i] = G

        except:
            pass
            # There are a million ways to get a div-by-zero or log-zero error
            # in that calculation. I could check them all, or just do this.
            # The vector was initialized with zeroes, which are the default
            # value I want for failed calculations anyhow.

    return dunningvector

def pure_rank_matrix(femalevectorsbyyear, malevectorsbyyear, datevector):
    rankmatrix = []
    magnitudematrix = []

    for i in datevector:
        d = dunnings(femalevectorsbyyear[i], malevectorsbyyear[i])

        # transform this into a nonparametric ranking
        decorated = [x for x in zip(d, [x for x in range(len(d))])]
        decorated.sort()

        negativeidx = -sum(d < 0)
        positiveidx = 1

        numzeros = sum(d == 0)

        ranking = np.zeros(len(d))
        for dvalue, index in decorated:
            # to understand what follows, it's crucial to remember that
            # we're iterating through decorated in dvalue order

            if dvalue < 0:
                ranking[index] = negativeidx
                negativeidx += 1
            elif dvalue > 0:
                ranking[index] = positiveidx
                positiveidx += 1
            else:
                # dvalue is zero
                pass

        checkzeros = sum(ranking == 0)
        if numzeros != checkzeros:
            print('error in number of zeros')


        rawmagnitude = femalevectorsbyyear[i] + malevectorsbyyear[i]
        normalizedmagnitude = rawmagnitude / np.sum(rawmagnitude)
        assert len(ranking) == len(normalizedmagnitude)
        rank_adjusted_by_magnitude = ranking * normalizedmagnitude

        rankmatrix.append(ranking)
        magnitudematrix.append(rank_adjusted_by_magnitude)

    return np.array(magnitudematrix), np.array(rankmatrix)

def diff_proportion(vecbyyear, datevector):
    diffmatrix = []

    for yr in datevector:
        mvec = (vecbyyear['m'][yr] * 5000) / np.sum(vecbyyear['m'][yr])
        fvec = (vecbyyear['f'][yr] * 5000) / np.sum(vecbyyear['f'][yr])
        dvec = fvec - mvec
        diffmatrix.append(dvec)

    return np.array(diffmatrix)

def normalized_dunning_matrix(femalevectorsbyyear, malevectorsbyyear, datevector):
    dmatrix = []

    for yr in datevector:
        mvec = (malevectorsbyyear[yr] * 10000) / np.sum(malevectorsbyyear[yr])
        fvec = (femalevectorsbyyear[yr] * 10000) / np.sum(femalevectorsbyyear[yr])
        dvec = dunnings(mvec, fvec)
        dmatrix.append(dvec)

    return np.array(dmatrix)

def ratio_matrix(femalevectorsbyyear, malevectorsbyyear, datevector):
    global wordsinorder
    rmatrix = []
    vlen = len(femalevectorsbyyear[1850])

    for yr in datevector:
        mvec = (malevectorsbyyear[yr] * 1000) / np.sum(malevectorsbyyear[yr])
        fvec = (femalevectorsbyyear[yr] * 1000) / np.sum(femalevectorsbyyear[yr])
        rvec = np.zeros(vlen)
        for i in range(vlen):
            if mvec[i] == 0 or fvec[i] == 0:
                continue
                # let it stay zero
            else:
                try:
                    rvec[i] = math.log((fvec[i] + 0.0001) / (mvec[i] + 0.001))
                except:
                    print(yr, fvec[i], mvec[i], wordsinorder[i])
        rmatrix.append(rvec)

    return np.array(rmatrix)

diffmatrix = diff_proportion(vecbyyear, datevector)

def writematrix(amatrix, outpath):
    global wordsinorder, datevector

    with open(outpath, mode = 'w', encoding = 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['thedate'] + wordsinorder)
        for i, date in enumerate(datevector):
            writer.writerow(np.insert(amatrix[i, : ], 0, date))

# writematrix(relative_freq_matrix, '../results/relativewordfreqs.csv')
writematrix(diffmatrix, '../dataforR/speechlessdiffmatrix.csv')
# writematrix(ratiomatrix, '../results/ratiomatrix.csv')
# writematrix(normaldunnings, '../results/dunningmatrix.csv')

# def magnitude_times_rank(femalevectorsbyyear, malevectorsbyyear, datevector):
#     dmatrix = []

#     for yr in datevector:
#         d = dunnings(femalevectorsbyyear[yr], malevectorsbyyear[yr])
#         rawmagnitude = femalevectorsbyyear[yr] + malevectorsbyyear[yr]
#         normalizedmagnitude = rawmagnitude / np.sum(rawmagnitude)

#         d = dunnings(femalevectorsbyyear[yr], malevectorsbyyear[yr])
#         normalized_d = d / np.sum(abs(d))

#         assert len(d) == len(rawmagnitude)
#         mtr = d * rawmagnitude
#         dmatrix.append(mtr)

#     return np.array(dmatrix)


# dunningmatrix, rankmatrix = pure_rank_matrix(femalevectorsbyyear, malevectorsbyyear, datevector)

print('Linear regression to infer slopes.')
datevector = np.array(datevector)
outrows = []
for i in range(VOCABLENGTH):
    thiscolumn = diffmatrix[ : , [i]]
    # note: the brackets around i extract it as a *column* rather than row

    notmissing = thiscolumn != 0
    # still a column

    y = thiscolumn[notmissing].transpose()

    # that's a cheap hack to create an array w/ more than one column,
    # which the linear regression seems to want

    x = datevector[notmissing.transpose()[0]]
    # We have to transpose the column "notmissing" to index a row.

    x = x[ : , np.newaxis]
    # Then we have to make x a row of an array with two
    # dimensions (even though it only has one row).

    vectorlen = len(x)

    word = wordsinorder[i]

    model = LinearRegression()

    model.fit(x, y)
    slope = model.coef_[0]
    intercept = model.intercept_
    standard_deviation = np.std(y)

    nineteenth = np.mean(thiscolumn[0:120])
    twentieth =np.mean(thiscolumn[120:])
    change = twentieth - nineteenth

    approachmid = abs(np.nanmean(thiscolumn[0:60])) - abs(np.nanmean(thiscolumn[150:210]))
    approachstd = approachmid / standard_deviation

    # note that it's important we use thiscolumn rather than y here, because y has been reduced
    # in length

    out = dict()
    out['word'] = word
    out['slope'] = slope
    out['mean'] = np.mean(thiscolumn)
    out['intercept'] = intercept
    out['change'] = change
    out['approachmid'] = approachmid
    out['approachstd'] = approachstd
    outrows.append(out)

with open('../dataforR/speechlessdiffslopes.csv', mode = 'w', encoding = 'utf-8') as f:
    writer = csv.DictWriter(f, fieldnames = ['word', 'slope', 'mean', 'intercept', 'change', 'approachmid', 'approachstd'])
    writer.writeheader()
    for row in outrows:
        writer.writerow(row)

# print('Writing results ...')
# with open('../results/magdunnings.csv', mode = 'w', encoding = 'utf-8') as f:
#     writer = csv.writer(f)
#     writer.writerow(wordsinorder)
#     for i in range(datecount):
#         thisrow = ['NA'] * VOCABLENGTH
#         for j in range(VOCABLENGTH):
#             thisval = dunningmatrix[i, j]
#             if thisval < - 0.00001 or thisval > 0.00001:
#                 thisrow[j] = thisval
#         writer.writerow(thisrow)

# print('Writing results ...')
# with open('../results/rawdunnings.csv', mode = 'w', encoding = 'utf-8') as f:
#     writer = csv.writer(f)
#     writer.writerow(wordsinorder)

#     rowsums = np.sum(abs(rankmatrix), axis = 1) / 3123750
#     # rescaled so that max should be ±2500

#     for i in range(datecount):
#         thisrow = ['NA'] * VOCABLENGTH
#         for j in range(VOCABLENGTH):
#             thisval = rankmatrix[i, j] / rowsums[i]
#             if thisval < -0.0001 or thisval > 0.0001:
#                 thisrow[j] = thisval
#         writer.writerow(thisrow)







