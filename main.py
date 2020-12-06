#!/usr/bin/env python3
import sys
import json
import pandas
import numpy
import matplotlib.pyplot as pyplot

uuid = sys.argv[1]

df_global = pandas.read_json(open('./issuu_cw2.json'), lines=True)
df_document = df_global[df_global.subject_doc_id == uuid]

def get_countries(df_document):
    return df_document.visitor_country.value_counts().rename_axis('visitor_country').reset_index(name='number_visitors')

def get_continents(df_countries):
    return 0

def get_browsers(df_global):
    refined_useragent = df_global.visitor_useragent.str.extract(r'(\w+)/.*$')
    df_global = df_global.assign(visitor_useragent=refined_useragent)
    
    return df_global.visitor_useragent.value_counts().rename_axis('visitor_browser').reset_index(name='number_visitors')

def get_top10_readers(df_global):
    df_pageandread = df_global[df_global.event_type == 'pagereadtime'][['visitor_uuid', 'event_readtime']]
    return pandas.DataFrame(df_pageandread.groupby(['visitor_uuid']).sum().sort_values('event_readtime').head(10))

def get_readers_uuids(df_global, doc_uuid):
    return pandas.Series(df_global[df_global.subject_doc_id == doc_uuid].visitor_uuid.unique())

def get_docs_read(df_global, visitor_uuid):
    return pandas.Series(df_global[df_global.visitor_uuid == visitor_uuid].subject_doc_id)

def get_alike(df_global, doc_uuid, user_uuid=0, sort_func=lambda df: df):
    df_read = df_global[df_global.event_type == 'read']
    sr_readers = get_readers_uuids(df_read, doc_uuid)
    sr_readers = sr_readers[sr_readers != user_uuid]

    list_series = []
    for usr in sr_readers:
        list_series.append(get_docs_read(df_global, usr))

    sr_alike = pandas.concat(list_series)
    sr_alike.dropna(inplace=True)
    return sr_alike[sr_alike != doc_uuid].value_counts()

def sort_df_asc(df_alike):
    return df_alike.sort_values(ascending=True)

def sort_df_desc(df_alike):
    return df_alike.sort_values(ascending=False)

def also_like(df_global, doc_uuid, user_uuid=0, sort_func=lambda df: df):
    return sort_func(get_alike(df_global, doc_uuid, user_uuid, sort_func).head(10))

fig, axes = pyplot.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

ax0.hist(get_countries(df_document.copy()))
ax0.set_title("Number of visitors by country")
ax0.set_xlabel("Country")
ax0.set_ylabel("Number of visitors")

ax1.hist(get_countries(df_document.copy()))
ax1.set_title("Number of visitors by continent")
ax1.set_xlabel("Continent")
ax1.set_ylabel("Number of visitors")

ax2.hist(get_browsers(df_global.copy()))
ax2.set_title("Number of visitors by brower")
ax2.set_xlabel("Browser")
ax2.set_ylabel("Number of visitors")

ax3.hist(get_top10_readers(df_global.copy()))
ax3.set_title("Most avid readers")
ax3.set_xlabel("Reader")
ax3.set_ylabel("Number of reads")

print(get_countries(df_document.copy()))