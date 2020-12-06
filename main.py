#!/usr/bin/env python3
import sys, getopt
import json
import pandas
import numpy
import matplotlib.pyplot as pyplot
import tkinter

g_df_global = g_df_document = g_df_continent = None
g_usr_uuid = g_doc_uuid = ''

def main(argv):
    global g_usr_uuid, g_doc_uuid 
    global g_df_global, g_df_document, g_df_continent

    g_usr_uuid, g_doc_uuid, file_name, task_id = check_input(argv)
    g_df_global, g_df_document, g_df_continent = init_dfs(file_name)

    if task_id == '2a':
        show_countries()
    elif task_id == '2b':
        show_continents()
    elif task_id == '3a':
        show_browsers()
    elif task_id == '3b':
        show_browsers_clean()
    elif task_id == '4':
        show_avid()
    elif task_id == '5d':
        show_also_like_list()
    elif task_id == '6':
        return
    elif task_id == '7':
        show_gui()

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

def init_dfs(file_name):
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
        df_document = df_global[df_global.subject_doc_id == g_doc_uuid]
        return df_global, df_document, df_continent

def help(err_code=0, err_msg='The correct usage is : cw2 -u user_uuid -d doc_uuid -t task_id -f file_name'):
    print('CW2 Help')
    print(err_msg)
    exit(err_code)

def get_countries():
    return g_df_document.visitor_country.value_counts().rename_axis('visitor_country').reset_index(name='number_visitors').set_index('visitor_country')

def get_continents():
    return pandas.merge(left=g_df_document, right=g_df_continent,  left_on='visitor_country', right_on='country_code').continent_code.value_counts().rename_axis('visitor_continent').reset_index(name='number_visitors').set_index('visitor_continent')

def get_browsers():    
    return g_df_global.visitor_useragent.value_counts().rename_axis('visitor_browser').reset_index(name='number_visitors').set_index('visitor_browser')

def get_browsers_clean():
    global g_df_global
    
    refined_useragent = g_df_global.visitor_useragent.str.extract(r'(\w+)/.*$')
    g_df_global = g_df_global.assign(visitor_useragent=refined_useragent)
    
    return g_df_global.visitor_useragent.value_counts().rename_axis('visitor_browser').reset_index(name='number_visitors').set_index('visitor_browser')

def get_top10_readers():
    df_pageandread = g_df_global[g_df_global.event_type == 'pagereadtime'][['visitor_uuid', 'event_readtime']]
    return pandas.DataFrame(df_pageandread.groupby(['visitor_uuid']).sum().sort_values('event_readtime').head(10))

def get_readers_uuids(df_read, document_uuid):
    return pandas.Series(g_df_global[g_df_global.subject_doc_id == document_uuid].visitor_uuid.unique())

def get_docs_read(visitor_uuid):
    return pandas.Series(g_df_global[g_df_global.visitor_uuid == visitor_uuid].subject_doc_id)

def get_alike(sort_func=lambda df: df):
    df_read = g_df_global[g_df_global.event_type == 'read']
    sr_readers = get_readers_uuids(df_read, g_doc_uuid)
    sr_readers = sr_readers[sr_readers != g_usr_uuid]

    list_series = []
    for usr in sr_readers:
        list_series.append(get_docs_read(usr))
    
    if len(list_series) < 1:
        return pandas.Series([])

    sr_alike = pandas.concat(list_series)
    sr_alike.dropna(inplace=True)
    return sr_alike[sr_alike != g_doc_uuid].value_counts() 

def sort_df_asc(df_alike):
    return df_alike.sort_values(ascending=True)

def sort_df_desc(df_alike):
    return df_alike.sort_values(ascending=False)

def also_like(sort_func=lambda df: df):
    return sort_func(get_alike(sort_func).head(10)).index.tolist()

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

def show_countries():
    show_bar_plot(get_countries(),'Number of visitors per country', 'Countries','Visitors')

def show_continents():
    show_bar_plot(get_continents(), 'Number of visitors per continent', 'Continents', 'Visitors')

def show_browsers():
    show_bar_plot(get_browsers(),'Number of visitors per browser', 'Browsers','Visitors')

def show_browsers_clean():
    show_bar_plot(get_browsers_clean(),'Number of visitors per browser', 'Browsers','Visitors')

def show_avid():
    show_bar_plot(get_top10_readers(), 'Most avid readers','Readers','Time read')

def show_also_like_list():
    list_also_like = also_like(sort_df_desc)
    also_like_text = 'Similar documents are :\n' + ',\n'.join(list_also_like) if len(list_also_like) > 0 else 'No similar doc were found'
    show_popup('Also like ' + g_doc_uuid, also_like_text)

def update_inputs(new_doc_uuid, new_usr_uuid, next_action):
    global g_usr_uuid, g_doc_uuid 
    global g_df_global, g_df_document, g_df_continent

    g_doc_uuid, g_usr_uuid = new_doc_uuid, new_usr_uuid
    g_df_document = g_df_global[g_df_global.subject_doc_id == g_doc_uuid]
    
    next_action()

def show_gui(): 
    window = tkinter.Tk()

    bt_countries = tkinter.Button(text="Visitors by countries", command=lambda: update_inputs(entry_doc.get(), entry_usr.get(), show_countries))
    bt_countries.pack()

    bt_continents = tkinter.Button(text="Visitors by continents", command=lambda: update_inputs(entry_doc.get(), entry_usr.get(), show_continents))
    bt_continents.pack()

    bt_browsers = tkinter.Button(text="Visitors by browsers", command=lambda: update_inputs(entry_doc.get(), entry_usr.get(), show_browsers_clean))
    bt_browsers.pack()

    bt_avid = tkinter.Button(text="Most avid readers", command=lambda: update_inputs(entry_doc.get(), entry_usr.get(), show_avid))
    bt_avid.pack()

    entry_doc = tkinter.Entry(window)
    entry_usr = tkinter.Entry(window)

    tkinter.Label(window, text="Doc UUID").pack()
    entry_doc.insert(0, g_doc_uuid)
    entry_doc.pack()
    
    tkinter.Label(window, text="User UUID").pack()
    entry_usr.insert(0, g_usr_uuid)
    entry_usr.pack()

    bt_alike_list = tkinter.Button(text="Show also like list", command=lambda: update_inputs(entry_doc.get(), entry_usr.get(), show_also_like_list))
    bt_alike_list.pack()

    bt_exit = tkinter.Button(text="Quit", command=exit)
    bt_exit.pack()

    window.mainloop()


if __name__ == "__main__":
   main(sys.argv[1:])