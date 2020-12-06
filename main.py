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

def get_readers_uuids(df_global, doc_uuid):
    return df_global[df_global.env_doc_id == doc_uuid].visitor_uuid.unique()

def get_docs_read(df_global, user_uuid):
    return df_global[df_global.visitor_uuid == user_uuid].env_doc_id.unique()

def get_like(df_global):
    return 0
    
get_countries(df_document).plot.bar()