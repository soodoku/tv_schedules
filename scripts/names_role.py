#!/usr/bin/env python
# coding: utf-8

"""
Next step is to get the gender and race of 'created_by', 'directed_by', 
'starring', 'presented_by', 'executive_producers', 'producers', 'composers'.
Two complications:

 a. There can be multiple names per field. 
 b. There are a few Python packages for it though none is very good but ok for 
    now --- just Google and use what is best.

One proposed solution:
 i. Create a CSV with just unique names with the following fields:

     ```
     name, field, row
     XYZ, executive_producers, 10
     ```
 ii. Then use Python package/API to get gender and race (I don't see any
     package for race --- I can do this at my end so don't spend too much time
     on this.)
 """

import argparse
import re
import pandas as pd
from nameparser import HumanName
from demographics import us_demographics


def extract_name(names, subregex=None):
    r = []
    for n in names.split('|'):
        # FIXME: ad-hoc fixup
        a = re.sub('\(.*\)', ' ', n)
        a = re.sub('Associate producers:', '', a)
        a = re.sub('\[not verified in body\]', ' ', a)
        a = re.sub('Based on the film by', ' ', a)
        a = re.sub('Based on traditional legends', ' ', a)
        a = re.sub('by arrangement with Dick Rubin Ltd', ' ', a)
        a = re.sub('et al', '', a)
        a = re.sub('[\d-]*.*\:', ' ', a)
        a = re.sub('-', ' ', a)
        a = re.sub('\[\d+\]', ' ', a)
        a = re.sub('\s+and\s+', '&', a)
        a = re.sub('\s+or\s+', '&', a)
        a = re.sub('\sfor\s.*\sProductions', ' ', a, flags=re.I)
        a = re.sub('Based.*\s+by\s+', ' ', a, flags=re.I)
        a = re.sub('Based.*\s+for\s+', ' ', a, flags=re.I)
        a = re.sub('\s+Based.*?$', ' ', a, flags=re.I)
        # substitute non-breaking space
        a = a.replace('\xc2\xa0', ' ')
        # more ad-hoc substitutions from external list
        if subregex is not None:
            for s in subregex:
                before = a
                a = re.sub(r'\b' + s[0], s[1], a)
                if a != before:
                    print("'%s' ==> '%s': '%s' ==> '%s'" % (s[0], s[1],
                                                            before, a))
        a = re.split(r'[,&/•]', a)
        for b in a:
            c = b.strip()
            if len(c.split()) > 1:
                r.append(c)
            else:
                # print out one-word name
                if len(c):
                    print("%s ==> '%s'" % (names, c))
    return r


def get_demographics(n):
    try:
        name = HumanName(n)
        me = us_demographics(name.first, name.last)
        gender = 'male' if me.male > me.female else 'female'
        race = 'black' if me.black > me.white else 'white'
        return pd.Series([gender, race])
    except:
        return pd.Series([None, None])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='US TV Schedule name parser')
    parser.add_argument('input', help='US TV Schedule with metadata')
    parser.add_argument('-o', '--out', required=True,
                        help='Output filename')
    parser.add_argument('-s', '--substitute', required=None, default=None,
                        help='Subtitute list (regular expression)')

    args = parser.parse_args()

    if args.substitute is not None:
        sub_df = pd.read_csv(args.substitute, header=None, dtype=str)
        sub_df.fillna('', inplace=True)
        subregex = sub_df.values.tolist()
    else:
        subregex = None

    df = pd.read_csv(args.input)

    # extract name fields for statistics
    name_fields = ['created_by', 'directed_by', 'starring', 'presented_by',
                   'executive_producers', 'producers', 'composers']

    # collect all names
    all_names = []
    for f in name_fields:
        for index, c in df[df[f].notnull()].iterrows():
            for n in extract_name(c[f], subregex):
                all_names.append((n, f, index))

    # convert to DataFrame
    ndf = pd.DataFrame(all_names)
    ndf.columns = ['name', 'field', 'index']
    ndf.drop_duplicates(inplace=True)

    # Get gender and race from demographics database
    ndf[['gender', 'race']] = ndf.name.apply(lambda c: get_demographics(c))

    # export names to file
    ndf.drop_duplicates(inplace=True)
    ndf.to_csv(args.out, index=False)
