#!/usr/bin/env python3

import sys,csv,re
import numpy as np
import pandas as pd

separatedataframes = []

def justthedate(astring):
    ''' Takes a badly encoded date and returns
    just the year part, which we want.
    '''

    date = astring[0:4]
    return date

with open('publishersweekly.csv', encoding = 'utf-8') as f:
    pw1 = pd.read_csv(f)
    subsetofpw1 = pw1.loc[ :, ['date', 'firstpub', 'author', 'title', 'htid', 'inhathi', 'gender']]
    separatedataframes.append(subsetofpw1)

with open('pubweekly1985.csv', encoding = 'utf-8') as f:
    pw2 = pd.read_csv(f)
    subsetofpw2 = pw2.loc[ :, ['date', 'firstpub', 'author', 'title', 'htid', 'inhathi', 'gender']]
    separatedataframes.append(subsetofpw2)

with open('tedcondensedpubweekly.csv', encoding = 'utf-8') as f:
    pw3 = pd.read_csv(f)
    pw3['date'] = pw3.date.apply(justthedate)
    subsetofpw3 = pw3.loc[ :, ['date', 'firstpub', 'author', 'title', 'htid', 'inhathi', 'gender']]
    separatedataframes.append(subsetofpw3)

with open('pubweekly1920.csv', encoding = 'utf-8') as f:
    pw4 = pd.read_csv(f)
    subsetofpw4 = pw4.loc[ :, ['date', 'firstpub', 'author', 'title', 'htid', 'inhathi', 'gender']]
    separatedataframes.append(subsetofpw4)

masterframe = pd.concat(separatedataframes)
masterframe.to_csv('masterpubweeklydata.csv', index = False)


