#!/usr/bin/env python3
import sys, getopt
import json
import pandas
import numpy
import matplotlib.pyplot as pyplot

import tkinter as tk

def main(argv):
    usr_uuid = ''
    doc_uuid = ''
    file_name = ''
    task_id = ''

    try:
        opts, args = getopt.getopt(argv,"hu:d:f:t:")
    except getopt.GetoptError:
        help(2)
    for opt, arg in opts:
        if opt == "-u":
            usr_uuid = arg
        elif opt == "-d":
            doc_uuid = arg
        elif opt == "-f":
            file_name = arg
        elif opt == "-t":
            task_id = arg
        elif opt == "-h":
            help(0)
        else:
            help(2)
    if usr_uuid == '' or doc_uuid == '' or file_name == '' or task_id == '':
        help(2)
    else:
        df_global = pandas.read_json(open('./issuu_cw2.json'), lines=True)
        df_continents = pandas.read_json(open('./continent.json'), typ='series').rename_axis('country_code').reset_index(name='continent_code')

        df_document = df_global[df_global.subject_doc_id == doc_uuid]
        show_gui(doc_uuid, usr_uuid)

def help(err_code=0):
    print('CW2 Help :')
    print('cw2 -u user_uuid -d doc_uuid -t task_id -f file_name')

def get_countries(df_document):
    return df_document.visitor_country.value_counts().rename_axis('visitor_country').reset_index(name='number_visitors').set_index('visitor_country')

def get_continents(df_document, df_continents):
    return pandas.merge(left=df_document, right=df_continents,  left_on='visitor_country', right_on='country_code').continent_code.value_counts().rename_axis('visitor_continent').reset_index(name='number_visitors').set_index('visitor_continent')

def get_browsers(df_global):
    refined_useragent = df_global.visitor_useragent.str.extract(r'(\w+)/.*$')
    df_global = df_global.assign(visitor_useragent=refined_useragent)
    
    return df_global.visitor_useragent.value_counts().rename_axis('visitor_browser').reset_index(name='number_visitors').set_index('visitor_browser')

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

def make_plot(df, title, label_x, label_y):
    df.plot(kind='bar', rot=0)
    pyplot.suptitle(title)
    pyplot.xlabel(label_x)
    pyplot.ylabel(label_y)
    pyplot.show()

def show_continents():
    make_plot(get_continents(df_document, df_continents), 'Number of visitors per continent', 'Continents', 'Visitors')
    
def show_countries():
    make_plot(get_countries(df_document.copy()),'Number of visitors per country', 'Countries','Visitors')

def show_browsers():
    make_plot(get_browsers(df_global.copy()),'Number of visitors per browser', 'Browsers','Visitors')

def show_avid():
    make_plot(get_top10_readers(df_global.copy()), 'Most avid readers','Readers','Time read')

def show_gui(doc_uuid, usr_uuid): 
    window = tk.Tk()

    label_doc = tk.Label(text="User-chosen document UUID :" + doc_uuid)
    label_doc.pack()
    label_usr = tk.Label(text="User-chosen user UUID :" + usr_uuid)
    label_usr.pack()

    bt_countries = tk.Button(text="Visitors by countries", command=show_countries)
    bt_countries.pack()

    bt_continents = tk.Button(text="Visitors by continents", command=show_continents)
    bt_continents.pack()

    bt_browsers = tk.Button(text="Visitors by browsers", command=show_browsers)
    bt_browsers.pack()

    window.mainloop()


if __name__ == "__main__":
   main(sys.argv[1:])