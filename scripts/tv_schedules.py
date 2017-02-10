#!/usr/bin/env python
# coding: utf-8

"""
Scrape all of the US television schedule data from Wikipedia at:
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


def table_to_list(table):
    dct = table_to_2d_dict(table)
    return list(iter_2d_dict(dct))


def table_to_2d_dict(table):
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
    if link is None or link.startswith('/w/index.php'):
        return None
    if link not in metadata:
        url = 'https://en.wikipedia.org' + link
        try:
            xdfs = pd.read_html(url, attrs={'class': 'infobox'},
                                flavor=['lxml', 'bs4'])
            meta = xdfs[0].to_json(orient='values')
            metadata[link] = meta
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
            return b[1]
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='US TV Schedule scraper')
    parser.add_argument('-o', '--out', required=True,
                        help='Output filename')
    args = parser.parse_args()

    url = 'https://en.wikipedia.org/wiki/Lists_of_United_States_network_television_schedules'
    html = requests.get(url).text
    patched_html = re.sub('<a.*?href="(.*?)".*>(.*?)</a>', '\\1', html)
    dfs = pd.read_html(patched_html, attrs={'class': 'wikitable'},
                       flavor=['bs4', 'lxml'])

    outputs = []
    types = ['prime time', 'daytime', 'late night', 'Saturday morning']
    for d in dfs:
        for r in d.iterrows():
            year = r[1][0]
            # FIXME: uncomment the following lines for quick test
            if year != u'2007–2008':
                continue
            for i, c in enumerate(r[1][1:]):
                tt = types[i]
                if not c.startswith('/w/'):
                    #print year, "==>", c
                    url = 'https://en.wikipedia.org' + c
                    html = requests.get(url).text
                    parsed = parse(StringIO(html.encode('utf-8')))
                    doc = parsed.getroot()
                    tables = doc.xpath(".//table[not(contains(@class, 'hlist') or contains(@class, 'vertical-navbox') or contains(@class, 'sortable'))]")
                    print len(tables), url
                    for t in tables:
                        for s in t.itersiblings(preceding=True):
                            if not s.tag.startswith('h'):
                                continue
                            h = s.findall('.//span')
                            day = h[0].text.strip()
                            break
                        ss = None
                        if s.tag == 'h3':
                            for s in t.itersiblings(preceding=True):
                                if s.tag != 'h2':
                                    continue
                                h = s.findall('.//span')
                                ss = h[0].text.strip()
                                if ss == 'Schedule':
                                    ss = None
                                #print ss, day
                                break
                        x = table_to_list(t)
                        current_channel = ''
                        for r in x[1:]:
                            opt = None
                            channel = r[0]
                            current_prog = ''
                            begin = ''
                            end = ''
                            for pi, p in enumerate(r[1:]):
                                if current_prog != p:
                                    if current_prog != '':
                                        end = x[0][pi + 1]
                                        if begin.strip().lower() in ['network', 'pm', 'am']:
                                            if current_prog != channel:
                                                opt = current_prog
                                        else:
                                            if day not in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
                                                if ss is None:
                                                    ss = day
                                                day = None
                                            #print year, tt, day, ss, channel, opt, current_prog, begin, end
                                            outputs.append((year, tt, day, ss, channel, opt, current_prog, begin, end))
                                    current_prog = p
                                    begin = x[0][pi + 1]                                    
                            end = '*' + x[0][-1]
                            if begin.strip().lower() not in ['network', 'pm', 'am', '']:
                                if day not in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
                                    if ss is None:
                                        ss = day
                                    day = None
                                #print year, tt, day, ss, channel, opt, current_prog, begin, end
                                outputs.append((year, tt, day, ss, channel, opt, current_prog, begin, end))
                    #break
            #break
        #break


    out_df = pd.DataFrame(outputs)
    out_df.columns = ['year', 'period', 'day', 'season', 'channel', 'channel_optional', 'program', 'begin', 'end']

    out_df['year'] = out_df.year.str.replace(u'–', '-')
    out_df['day'] = out_df.day.str.replace(u'–', '-')
    out_df['season'] = out_df.season.str.replace(u'–', '-')

    # extract meta_link and remove the magics
    out_df['meta_link'] = out_df.program.apply(lambda c: extract_meta_link(c))
    out_df.program = out_df.program.str.replace(r'<<.*>>', '')
    out_df.channel = out_df.channel.str.replace(r'<<.*>>', '')
    out_df.channel_optional = out_df.channel_optional.str.replace(r'<<.*>>', '')

    # scrape meta data and keep in json format
    # FIXME:  do these in another script "tv_schedules_meta.py"
    #out_df['meta'] = out_df.meta_link.apply(lambda c: scrape_meta(c))

    # extract genre from meta data
    #out_df['genre'] = out_df.meta.apply(lambda c: get_json_value(c, 'Genre'))

    out_df.drop_duplicates(inplace=True)

    """
    Issue #2:
        If season is empty and if channel_optional has words "Fall, Spring, 
        Winter, Summer" in it, take the data from channel_optional field to
        season field. And clear channel_optional field.
    """
    out_df.loc[out_df.season.isnull() & out_df.channel_optional.isin(['Fall', 'Spring', 'Winter', 'Summer']), 'season'] = out_df.loc[out_df.season.isnull() & out_df.channel_optional.isin(['Fall', 'Spring', 'Winter', 'Summer']), 'channel_optional']
    out_df.loc[out_df.season == out_df.channel_optional, 'channel_optional'] = None

    out_df.to_csv(args.out, index_label='no', encoding='utf-8')
