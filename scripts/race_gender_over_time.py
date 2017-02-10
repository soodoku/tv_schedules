#!/usr/bin/env python
# coding: utf-8

"""
Create a new CSV that uses data from the names file and the show file with the
following fields:

for each year (aggregate over each year):

 year, 
 prop1_female_producers (proportion of shows with at least one female producer = 
 total number of shows with at least one female producer/total number of shows), 
 prop1_female_directors (proportion of shows with at least one female director), 
 prop1_female_creators (proportion of shows with at least one female creator), 
 prop_female_producers (total number of female producers divided by total number of producers), 
 prop_female_directors (total number of female directors divided by total number of directors), 
 prop_female_creators (total number of female creators divided by total number of creators), 
 prop_female_cast (total number of female cast members/total number of cast members),
 prop_female_presenters (total number of female presenters divided by total number of presenters), 
 prop1_black_producers,
 ....
 """

import argparse
import pandas as pd


alias = {'created_by': 'creators',
         'directed_by': 'directors',
         'presented_by': 'presenters',
         'starring': 'cast'}


def get_alias_name(p, c):
    if c in alias:
        a = alias[c]
    else:
        a = c
    return '_'.join([p, a])


def get_race(p, f=1.0):
    return 'black' if (p * f) > 0.5 else 'white'


def get_gender(p, f=1.0):
    return 'female' if (p * f) > 0.5 else 'male'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='US TV Schedule name proportion')
    parser.add_argument('input', help='US TV Schedule name with gender and race')
    parser.add_argument('-m', '--meta', required=True,
                        help='US TV Schedule data with meta data')
    parser.add_argument('-g', '--gender', default='gender',
                        help="Gender column name (default='gender')")
    parser.add_argument('-r', '--race', default='race',
                        help="Race column name (default='race')")
    parser.add_argument('-o', '--out', required=True,
                        help='Output filename')

    args = parser.parse_args()

    df = pd.read_csv(args.meta, usecols=['year'])

    ndf = pd.read_csv(args.input, usecols=['name', 'field', 'index',
                                           args.gender, args.race])

    # join 'year' column
    ndf = ndf.join(df, on='index')

    # try to conver the percent of female to gender
    if ndf[args.gender].dtype == 'float64':
        f = 0.01 if len(ndf[ndf[args.gender] > 1]) > 0 else 1.0
        ndf[args.gender] = ndf[args.gender].apply(lambda c: get_gender(c, f))

    # try to convert the percent of black to race
    if ndf[args.race].dtype == 'float64':
        f = 0.01 if len(ndf[ndf[args.race] > 1]) > 0 else 1.0
        ndf[args.race] = ndf[args.race].apply(lambda c: get_race(c, f))

    # extract name fields for statistics
    name_fields = ['created_by', 'directed_by', 'starring', 'presented_by',
                   'executive_producers', 'producers', 'composers']

    # Count
    prop1_female = ndf.groupby(['year', 'field', args.gender]).agg({'index': lambda x: x.nunique()}).unstack()
    prop_female = ndf.groupby(['year', 'field', args.gender]).agg({'name': lambda x: x.nunique()}).unstack()
    prop1_black = ndf.groupby(['year', 'field', args.race]).agg({'index': lambda x: x.nunique()}).unstack()
    prop_black = ndf.groupby(['year', 'field', args.race]).agg({'name': lambda x: x.nunique()}).unstack()

    # Calculation the proportion
    odf = None
    for p, xdf in [('prop1_female', prop1_female), ('prop_female', prop_female), ('prop1_black', prop1_black), ('prop_black', prop_black)]:
        xdf.reset_index(level=[1, 0], inplace=True)
        xdf.columns = ['year', 'field', 'a', 'b']
        xdf['a'].fillna(0, inplace=True)
        xdf['total'] = xdf['a'] + xdf['b']
        xdf['prop'] = xdf['a'] / xdf['total']
        xdf['alias'] = xdf.field.apply(lambda c: get_alias_name(p, c))
        if odf is None:
            odf = xdf
        else:
            odf = odf.append(xdf)

    # Output
    rdf = odf[['year', 'alias', 'prop']].pivot(index='year', columns='alias', values='prop')
    rdf.to_csv(args.out, index_label='year', encoding='utf-8')
