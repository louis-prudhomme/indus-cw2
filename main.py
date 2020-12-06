#!/usr/bin/env python3
import sys
import json
import pandas

uuid = sys.argv[1]

df = pandas.read_json(open('./issuu_sample.json'), lines=True)

df_document = df[df.env_doc_id == uuid]

df_countries = df['visitor_country'].value_counts()

refined_useragent = df_document.visitor_useragent.str.extract(r'(\w+)/.*$')
df_document = df_document.assign(visitor_useragent=refined_useragent)
df_browsers = df_document['visitor_useragent'].value_counts()

print(df_document)
print(df_countries)
print(df_browsers)