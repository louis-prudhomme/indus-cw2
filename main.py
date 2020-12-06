#!/usr/bin/env python3
import sys, getopt
import json
import pandas
import numpy
import matplotlib.pyplot as pyplot
import tkinter

def main(argv):
    usr_uuid, doc_uuid, file_name, task_id = check_input(argv)
    df_global, df_document, df_continent = init_dfs(file_name, doc_uuid)

    if task_id == '2a':
        show_countries(df_document)
    elif task_id == '2b':
        show_continents(df_document, df_continent)
    elif task_id == '3a':
        show_browsers(df_global)
    elif task_id == '3b':
        show_browsers_clean(df_global)
    elif task_id == '4':
        show_avid(df_global)
    elif task_id == '5d':
        show_also_like_list(df_global, doc_uuid, usr_uuid)
    elif task_id == '6':
        return
    elif task_id == '7':
        show_gui(df_global, df_document, df_continent, doc_uuid, usr_uuid)

def show_popup(title, msg):
    tkinter.messagebox.showinfo(title, msg)

def check_input(argv):
    usr_uuid = doc_uuid = file_name = task_id = ''
    valid_task_ids = ['2a', '2b', '3a', '3b', '4', '5d', '6', '7']
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
    elif task_id not in valid_task_ids:
        help(2, 'Provided task is invalid, valid tasks are ' + ' '.join(valid_task_ids))
    else:
        return usr_uuid, doc_uuid, file_name, task_id

def init_dfs(file_name, doc_uuid):
    try: 
        print('Obtaining dataset, please wait')
        df_global = pandas.read_json(file_name, lines=True)
        print('Obtaining continent file, please wait')
        df_continent = pandas.read_json('http://country.io/continent.json', typ='series').rename_axis('country_code').reset_index(name='continent_code')
    except OSError as err:
        help(1, 'Cannot open files: {0}'.format(err))
    except ValueError as err:
        help(2, 'Please check the provided file: {0}'.format(err))
    else:
        df_document = df_global[df_global.subject_doc_id == doc_uuid]
        return df_global, df_document, df_continent

def help(err_code=0, err_msg='The correct usage is : cw2 -u user_uuid -d doc_uuid -t task_id -f file_name'):
    print('CW2 Help')
    print(err_msg)
    exit(err_code)

def get_countries(df_document):
    return df_document.visitor_country.value_counts().rename_axis('visitor_country').reset_index(name='number_visitors').set_index('visitor_country')

def get_continents(df_document, df_continent):
    return pandas.merge(left=df_document, right=df_continent,  left_on='visitor_country', right_on='country_code').continent_code.value_counts().rename_axis('visitor_continent').reset_index(name='number_visitors').set_index('visitor_continent')

def get_browsers(df_global):    
    return df_global.visitor_useragent.value_counts().rename_axis('visitor_browser').reset_index(name='number_visitors').set_index('visitor_browser')


def get_browsers_clean(df_global):
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
    
    if len(list_series) < 1:
        return pandas.Series([])

    sr_alike = pandas.concat(list_series)
    sr_alike.dropna(inplace=True)
    return sr_alike[sr_alike != doc_uuid].value_counts() 

def sort_df_asc(df_alike):
    return df_alike.sort_values(ascending=True)

def sort_df_desc(df_alike):
    return df_alike.sort_values(ascending=False)

def also_like(df_global, doc_uuid, user_uuid=0, sort_func=lambda df: df):
    return sort_func(get_alike(df_global, doc_uuid, user_uuid, sort_func).head(10)).index.tolist()

def make_plot(df, title, label_x, label_y):
    df.plot(kind='bar', rot=0)
    pyplot.suptitle(title)
    pyplot.xlabel(label_x)
    pyplot.ylabel(label_y)
    pyplot.show()
    
def show_bar_plot(df, title, x, y):
    if df.shape[0] > 0:
        make_plot(df, title, x, y)
    else:
        show_popup('Nothing found', 'No data was found for these criterias')

def show_countries(df_document):
    show_bar_plot(get_countries(df_document),'Number of visitors per country', 'Countries','Visitors')

def show_continents(df_document, df_continent):
    show_bar_plot(get_continents(df_document, df_continent), 'Number of visitors per continent', 'Continents', 'Visitors')

def show_browsers(df_global):
    show_bar_plot(get_browsers(df_global),'Number of visitors per browser', 'Browsers','Visitors')

def show_browsers_clean(df_global):
    show_bar_plot(get_browsers_clean(df_global),'Number of visitors per browser', 'Browsers','Visitors')

def show_avid(df_global):
    show_bar_plot(get_top10_readers(df_global), 'Most avid readers','Readers','Time read')

def show_also_like_list(df_global, doc_uuid, user_uuid):
    list_also_like = also_like(df_global, doc_uuid, user_uuid, sort_df_desc)
    also_like_text = 'Similar documents are :\n' + ',\n'.join(list_also_like) if len(list_also_like) > 0 else 'No similar doc were found'
    show_popup('Also like ' + doc_uuid, also_like_text)

def show_gui(df_global, df_document, df_continent, doc_uuid, usr_uuid): 
    window = tkinter.Tk()

    bt_countries = tkinter.Button(text="Visitors by countries", command=lambda: show_countries(df_document))
    bt_countries.pack()

    bt_continents = tkinter.Button(text="Visitors by continents", command=lambda: show_continents(df_document, df_continent))
    bt_continents.pack()

    bt_browsers = tkinter.Button(text="Visitors by browsers", command=lambda: show_browsers_clean(df_global))
    bt_browsers.pack()

    bt_avid = tkinter.Button(text="Most avid readers", command=lambda: show_avid(df_global))
    bt_avid.pack()
    
    label_doc = tkinter.Label(text="User-chosen document UUID :" + doc_uuid)
    label_doc.pack()
    label_usr = tkinter.Label(text="User-chosen user UUID :" + usr_uuid)
    label_usr.pack()

    entry_doc = tkinter.Entry(window)
    entry_usr = tkinter.Entry(window)

    tkinter.Label(window, text="Doc UUID").pack()
    entry_doc.insert(0, doc_uuid)
    entry_doc.pack()
    
    tkinter.Label(window, text="User UUID").pack()
    entry_usr.insert(0, usr_uuid)
    entry_usr.pack()

    bt_alike_list = tkinter.Button(text="Show also like list", command=lambda: show_also_like_list(df_global, entry_doc.get(), entry_usr.get()))
    bt_alike_list.pack()

    bt_exit = tkinter.Button(text="Quit", command=exit)
    bt_exit.pack()

    window.mainloop()


if __name__ == "__main__":
   main(sys.argv[1:])