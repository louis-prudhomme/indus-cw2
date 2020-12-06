#!/usr/bin/env python3
import sys
import json
import pandas
import matplotlib.pyplot as pyplot

uuid = sys.argv[1]

df_global = pandas.read_json(open('./issuu_sample.json'), lines=True)
df_document = df_global[df_global.env_doc_id == uuid]

def get_countries(df_document):
    return df_document.visitor_country.value_counts()

def get_continents(df_countries):
    return 0

def get_browsers(df_global):
    refined_useragent = df_global.visitor_useragent.str.extract(r'(\w+)/.*$')
    df_global = df_global.assign(visitor_useragent=refined_useragent)
    return df_global.visitor_useragent.value_counts()

def get_top10_readers(df_global):
    df_pageandread = df_global[df_global.event_type == 'pagereadtime'][['visitor_uuid', 'event_readtime']]
    return df_pageandread.groupby(['visitor_uuid']).sum().sort_values('event_readtime').head(10)

fig, axes = pyplot.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

ax0.hist(get_countries(df_document))
ax0.set_title("Number of visitors by country")
ax0.set_xlabel("Country")
ax0.set_ylabel("Number of visitors")

ax1.hist(get_countries(df_document))
ax1.set_title("Number of visitors by continent")
ax1.set_xlabel("Country")
ax1.set_ylabel("Number of visitors")

ax2.hist(get_browsers(df_global))
ax2.set_title("Number of visitors by browser")
ax2.set_xlabel("Browser")
ax2.set_ylabel("Number of visitors")

ax3.hist(get_top10_readers(df_global))
ax3.set_title("Top 10 avid readers")
ax3.set_xlabel("Browser")
ax3.set_ylabel("Number of visitors")

pyplot.show()