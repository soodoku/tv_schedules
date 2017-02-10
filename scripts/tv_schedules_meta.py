#!/usr/bin/env python
# coding: utf-8

"""
Scrapes meta data of the US television schedule data from Wikipedia at:
https://en.wikipedia.org/wiki/Category:United_States_television_schedules
Final format: Year, Channel, Day, Start Time, End Time
"""

import argparse
import re
import json
import requests
import pandas as pd
from cStringIO import StringIO
from lxml.html import parse
from pandas.io.parsers import TextParser
from collections import defaultdict
from pprint import pprint


# Global variable to keep unique metadata
metadata = dict()


def table_to_list(table, with_link=True):
    dct = table_to_2d_dict(table, with_link)
    return list(iter_2d_dict(dct))


def table_to_2d_dict(table, with_link=True):
    result = defaultdict(lambda: defaultdict(unicode))
    for row_i, row in enumerate(table.xpath('./tr')):
        for col_i, col in enumerate(row.xpath('./td|./th')):
            try:
                colspan = int(col.get('colspan', 1))
            except:
                colspan = 1
            try:
                rowspan = int(col.get('rowspan', 1))
            except:
                rowspan = 1
            col_data = col.text_content()
            # Issue #3: Add link magic
            if with_link:
                links = col.findall('.//a')
                if len(links):
                    col_data += "<<%s>>" % links[0].get('href')
            while row_i in result and col_i in result[row_i]:
                col_i += 1
            for i in range(row_i, row_i + rowspan):
                for j in range(col_i, col_i + colspan):
                    result[i][j] = col_data
    return result


def iter_2d_dict(dct):
    for i, row in sorted(dct.items()):
        cols = []
        for j, col in sorted(row.items()):
            cols.append(col)
        yield cols


def _unpack(row, kind='td'):
    """ similar to pd.read_html
    """
    if kind != 'th':
        elts = row.findall('.//th')
    else:
        elts = []
    elts += row.findall('.//%s' % kind)
    cols = []
    for e in elts:
        try:
            span = int(e.attrib['colspan'])
        except:
            span = 1
        for i in range(span):
            cols.append(e.text_content())
    return cols


def parse_options_data(table):
    rows = table.findall('.//tr')
    header = _unpack(rows[0], kind='th')
    data = [_unpack(r) for r in rows[1:]]
    return TextParser(data, names=header).get_chunk()


def extract_meta_link(c):
    m = re.match(r".*<<(.*)>>", c)
    if m:
        return m.group(1)
    return None


def scrape_meta(link):
    global metadata
    if link is None  or link.startswith('/w/index.php'):
        return None
    if link not in metadata:
        url = 'https://en.wikipedia.org' + link
        print link
        try:
            html = requests.get(url).text
            parsed = parse(StringIO(html.encode('utf-8')))
            doc = parsed.getroot()
            tables = doc.xpath(".//table[contains(@class, 'infobox')]")
            tt = []
            if len(tables):
                tt = table_to_list(tables[0], with_link=False)
                for t in tt:
                    if len(t) == 2:
                        t[0] = t[0].strip()
                        t[1] = t[1].strip().split('\n')
            metadata[link] = json.dumps(tt)
        except Exception as e:
            print link
            print e
            metadata[link] = None
    return metadata[link]


def get_json_value(c, key):
    if c is None:
        return None
    a = json.loads(c)
    for b in a:
        if b[0] == key:
            return '|'.join(b[1])
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='US TV Schedule metadata scraper')
    parser.add_argument('input', help='US TV Schedule data with meta link')
    parser.add_argument('-o', '--out', required=True,
                        help='Output filename')
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    # scrape meta data and keep in json format
    df.loc[df.meta_link.notnull(), 'meta'] = df.loc[df.meta_link.notnull(), 'meta_link'].apply(lambda c: scrape_meta(c))

    # extract additional fields from meta data
    fields = ['Audio format', 'Picture format', 'Created by', 'Directed by', 'Starring', 'Presented by', 'Executive producer(s)', 'Producer(s)', 'Composer(s)', 'Genre', 'Running time']
    keys = []
    for a in fields:
        a = a.lower()
        a = a.replace(' ', '_')
        a = a.replace('(', '')
        a = a.replace(')', '')
        keys.append(a)

    for a, b in zip(keys, fields):
        df.loc[df.meta.notnull(), a] = df.loc[df.meta.notnull(), 'meta'].apply(lambda c: get_json_value(c, b))

    # fix unicode 'running_time'
    df['running_time'] = df['running_time'].str.replace(u'\u2012', '-')
    df['running_time'] = df['running_time'].str.replace(u'\u2013', '-')
    df['running_time'] = df['running_time'].str.replace(u'\u2014', '-')
    df['running_time'] = df['running_time'].str.replace(u'\u2212', '-')
    df['running_time'] = df['running_time'].str.replace(u'\u2248', '~')
    df['running_time'] = df['running_time'].str.replace(u'\xa0', ' ')
    df['running_time'] = df['running_time'].str.replace(u'\xbd', ' 1/2 ')

    df.to_csv(args.out, index=False, encoding='utf-8')
