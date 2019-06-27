# The modol of the GUI
# That class control the logic of the GUI and is association with the system
# The function in this class are the "on action" function of any button of the gui
import datetime
import os
import pickle
import threading
from tkinter.messagebox import showinfo, showwarning
import Indexer
from tkinter import filedialog

import Parse
import ReadFile
import Searcher

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True


corpus_path = ""  # the path of the corpus
queries_path = ""  # the path of the queries
dist_path = ""  # the path to save the output
list_of_language = []  # the language in the corpus
list_of_city = [] # the city in the corpus
stemmer = False  # boolean that represent if the user ask for stemming
term_dictionary_in_corpus = {}  # all the terms in the corpus and there frequency
in_process = False  # boolean that represent if the system still in progress
semantic = False

language_choice = []
city_choice = []
query_res = {}


def browseCorpuse():
    global corpus_path
    global in_process
    global w

    if not in_process:
        corpus_path = filedialog.askdirectory(title="Choose dir")
        w.Entry1.insert(0, corpus_path)


def browse_queries():
    global queries_path
    global in_process
    global w

    if not in_process:
        queries_path = filedialog.askopenfilename(title="Choose file")
        w.Entry3.insert(0, queries_path)


def run_query():
    global dist_path
    global w
    global term_dictionary_in_corpus
    global stemmer
    global semantic
    global language_choice
    global city_choice
    global query_res

    if not in_process:
        dist_path = w.Entry2.get()
        if stemmer:
            exists = os.path.isfile(dist_path + "/term_dictionary_stemmer.pkl")
        else:
            exists = os.path.isfile(dist_path + "/term_dictionary.pkl")
        if not exists or len(term_dictionary_in_corpus) == 0:
            showwarning('Warning', 'Please create the engine before or upload a dictionary.')
        else:
            query = w.Entry4.get()
            if query == "":
                showwarning('Warning', 'Please enter a query into the appropriate text cell.')
            else:
                def rank_query():
                    global query_res

                    reset_lists_on_screen_query()
                    query_res = Searcher.search(dist_path, query, stemmer, "", language_choice, city_choice, semantic)
                    fill_query_list()
                    bord_state('normal')
                    showinfo('info', 'Finished to find documents for query.')

                t = threading.Thread(target=rank_query)
                t.start()
                bord_state('disable')
                showinfo('info', 'Starting to find documents for query.')


def run_query_file():
    global dist_path
    global w
    global term_dictionary_in_corpus
    global stemmer
    global semantic
    global list_of_language
    global list_of_city
    global query_res

    if not in_process:
        if stemmer:
            exists = os.path.isfile(dist_path + "/term_dictionary_stemmer.pkl")
        else:
            exists = os.path.isfile(dist_path + "/term_dictionary.pkl")
        if not exists and not len(term_dictionary_in_corpus) == 0:
            showwarning('Warning', 'Please create the engine before or upload a dictionary.')
        else:
            query_path = w.Entry3.get()
            if query_path == "":
                showwarning('Warning', 'Please enter a path to queries file into the appropriate text cell.')
            else:
                if not os.path.isfile(query_path):
                    showwarning('Warning', 'queries file not exists.')
                else:
                    def rank_query():
                        global query_res
                        global language_choice
                        global city_choice

                        reset_lists_on_screen_query()
                        query_res = Searcher.search(dist_path, "", stemmer, query_path, language_choice, city_choice, semantic)
                        fill_query_list()
                        bord_state('normal')
                        showinfo('info', 'Finished to find documents for queries.')
                    t = threading.Thread(target=rank_query)
                    t.start()
                    bord_state('disable')
                    showinfo('info', 'Starting to find documents for query.')


def browseDestination():
    global dist_path
    global in_process
    global w

    if not in_process:
        dist_path = filedialog.askdirectory(title="Choose dir")
        w.Entry2.insert(0, dist_path)


def insertButton():
    global stemmer
    global dist_path
    global corpus_path
    global list_of_language
    global w
    global in_process

    if not in_process:
        corpus_path = w.Entry1.get()
        dist_path = w.Entry2.get()
        if corpus_path =="" or dist_path == "":
            showwarning('Warning', 'Please insert path to corpus and to save files.')
        else:
            def build_engine():
                global stemmer
                global dist_path
                global corpus_path
                global root
                global w
                global in_process
                global term_dictionary_in_corpus

                reset_lists_on_screen_language()
                reset_lists_on_screen_city()
                reset_lists_on_screen_query()
                total = datetime.datetime.now()
                term_dictionary = {}
                num_of_post = Indexer.start_read(corpus_path, dist_path, term_dictionary, stemmer)
                Indexer.extract_entity(term_dictionary, dist_path, num_of_post)
                num_of_doc = Indexer.merge_document_dictionary(dist_path, num_of_post, stemmer)
                t1 = threading.Thread(target=fill_language_list)
                t1.start()

                t2 = threading.Thread(target=fill_city_list)
                t2.start()

                Indexer.new_merge(dist_path, term_dictionary, num_of_post, stemmer)
                sort_key = sorted(term_dictionary)
                sort_term_dictionary = {}
                for key in sort_key:
                    sort_term_dictionary[key] = term_dictionary[key]
                if stemmer:
                    file = open(dist_path + "/term_dictionary_stemmer.pkl", "wb+")
                else:
                    file = open(dist_path + "/term_dictionary.pkl", "wb+")
                pickle.dump(sort_term_dictionary, file, pickle.HIGHEST_PROTOCOL)
                term_dictionary_in_corpus = sort_term_dictionary
                file.close()
                num_of_terms = len(sort_term_dictionary)
                total_time = str(datetime.datetime.now() - total)
                showinfo('info', 'The number of documents in corpus: ' + str(num_of_doc) + '\r\n' +
                         'The number of terms in the corpus: ' + str(num_of_terms) + '\r\n' +
                         'The total time: ' + str(total_time))
                bord_state('normal')

            t = threading.Thread(target=build_engine)
            t.start()
            bord_state('disable')
            showinfo('info', 'Build the engine will take about 25 minutes.' + '\r\n' +
                     'When the process is finished the window keys will be released.' + '\r\n' +
                     'You can go make a cup of coffee in the meantime.')


def bord_state(state):
    global w
    global in_process

    if state == 'disable':
        in_process = True
    else:
        in_process = False
    w.insert_btn.configure(state=state)
    w.resert_btn.configure(state=state)
    w.show_btn.configure(state=state)
    w.upload_btn.configure(state=state)
    w.stem_cbox.configure(state=state)
    w.semantic_cbox.configure(state=state)
    w.corpus_btn.configure(state=state)
    w.Button2.configure(state=state)
    w.reset_city_choice.configure(state=state)
    w.reset_language_choice.configure(state=state)
    w.queries_path_btn.configure(state=state)
    w.query_btn.configure(state=state)
    w.queries_run_btn.configure(state=state)
    w.add_language_choice.configure(state=state)
    w.add_city_choice.configure(state=state)
    w.query_res_btn.configure(state=state)
    w.query_res_save_all.configure(state=state)


def add_language():
    global in_process
    global w
    global language_choice

    if not in_process:
        language = w.string_var_language.get()
        if language not in language_choice and not language == "Select a language":
            language_choice.append(language)
            showinfo('info', language + ' add successfully')

def add_city():
    global in_process
    global w
    global city_choice

    if not in_process:
        city = w.string_var_city.get()
        if city not in city_choice and not city == "Select a city":
            city_choice.append(city)
            showinfo('info', city + ' add successfully')


def fill_language_list():
    global list_of_language
    global dist_path
    global w
    global top_level

    if stemmer:
        file = open(dist_path + "/document_dictionary_stemmer.pkl", "rb+")
    else:
        file = open(dist_path + "/document_dictionary.pkl", "rb+")
    document_dictionary = pickle.load(file)
    file.close()
    for key in document_dictionary:
        language = document_dictionary[key].language
        if not language in list_of_language:
            if not language.isnumeric() and not language == "":
                list_of_language.append(language)
    list_of_language = sorted(list_of_language)
    if len(list_of_language) == 0:
        list_of_language.append("Select a language")
    w.Listbox1.destroy()
    w.string_var_language = tk.StringVar()
    w.string_var_language.set("Select a language")
    w.Listbox1 = tk.OptionMenu(top_level, w.string_var_language, *list_of_language)
    w.Listbox1.place(relx=0.35, rely=0.556, relheight=0.05, relwidth=0.3)
    w.Listbox1.configure(background="white")
    w.Listbox1.configure(disabledforeground="#a3a3a3")
    w.Listbox1.configure(font="TkFixedFont")
    w.Listbox1.configure(foreground="#000000")
    w.Listbox1.configure(highlightbackground="#d9d9d9")
    w.Listbox1.configure(highlightcolor="black")
    w.Listbox1.configure(width=10)


def fill_city_list():
    global list_of_city
    global dist_path
    global w
    global top_level

    if stemmer:
        file = open(dist_path + "/city_dictionary_stemmer" + ".pkl", "rb+")
    else:
        file = open(dist_path + "/city_dictionary" + ".pkl", "rb+")
    city_dictionary = pickle.load(file)
    file.close()
    for city in city_dictionary:
        if not city in list_of_city:
            if not city.isnumeric() and not city == "":
                city = city[0].upper() + city[1:len(city)]
                list_of_city.append(city)
    list_of_city = sorted(list_of_city)
    if len(list_of_city) == 0:
        list_of_city.append("Select a city")
    w.Listbox2.destroy()
    w.string_var_city = tk.StringVar()
    w.string_var_city.set("Select a city")
    w.Listbox2 = tk.OptionMenu(top_level, w.string_var_city, *list_of_city)
    w.Listbox2.place(relx=0.68, rely=0.556, relheight=0.05, relwidth=0.25)
    w.Listbox2.configure(background="white")
    w.Listbox2.configure(disabledforeground="#a3a3a3")
    w.Listbox2.configure(font="TkFixedFont")
    w.Listbox2.configure(foreground="#000000")
    w.Listbox2.configure(highlightbackground="#d9d9d9")
    w.Listbox2.configure(highlightcolor="black")
    w.Listbox2.configure(width=10)

    reset_lists_on_screen_query()

def fill_query_list():
    global query_res
    global w
    global top_level

    list_of_query = []
    for query in query_res:
        list_of_query.append(query.replace('post', ""))
    list_of_query = sorted(list_of_query)
    w.Listbox3.destroy()
    w.string_var_query = tk.StringVar()
    w.string_var_query.set("Select a query number")
    w.Listbox3 = tk.OptionMenu(top_level, w.string_var_query, *list_of_query)
    w.Listbox3.place(relx=0.4, rely=0.885, relheight=0.05, relwidth=0.35)
    w.Listbox3.configure(background="white")
    w.Listbox3.configure(disabledforeground="#a3a3a3")
    w.Listbox3.configure(font="TkFixedFont")
    w.Listbox3.configure(foreground="#000000")
    w.Listbox3.configure(highlightbackground="#d9d9d9")
    w.Listbox3.configure(highlightcolor="black")
    w.Listbox3.configure(width=10)


def resetButton():
    global corpus_path
    global dist_path
    global list_of_language
    global stemmer
    global term_dictionary_in_corpus
    global w
    global top_level
    global in_process
    global city_choice
    global language_choice
    global query_res

    if not in_process:
        if dist_path == "":
            showwarning('Warning', 'Please insert Path to save files.')
        else:
            file_list = os.listdir(dist_path)
            if stemmer:
                for file in file_list:
                    if "stemmer" in file and not "stop_words" in file:
                        os.remove(dist_path + "/" + file)
            else:
                for file in file_list:
                    if not "stemmer" in file and not "stop_words" in file:
                        os.remove(dist_path + "/" + file)
            ReadFile.path = ""
            ReadFile.docNumList.clear()
            ReadFile.docCityList.clear()
            ReadFile.docLanguageList.clear()
            ReadFile.docTitleList.clear()
            ReadFile.docDateList.clear()
            ReadFile.textList.clear()
            ReadFile.textDic.clear()
            ReadFile.docDictionary.clear()
            ReadFile.length = 0
            ReadFile.fileName = ""
            ReadFile.index = 0
            ReadFile.corpus_city_dictionary.clear()
            ReadFile.world_city_dictionary.clear()
            Parse.__stop_words = ''
            Parse.__stemmer = False
            Parse.stemmer_dictionary.clear()
            corpus_path = ""
            dist_path = ""
            list_of_language.clear()
            term_dictionary_in_corpus.clear()
            w.Entry1.delete (0, tk.END)
            w.Entry2.delete (0, tk.END)
            w.Entry3.delete(0, tk.END)
            w.Entry4.delete(0, tk.END)
            city_choice.clear()
            language_choice.clear()
            query_res.clear()

            reset_lists_on_screen_language()
            reset_lists_on_screen_city()
            reset_lists_on_screen_query()

            showinfo('info', 'Reset completed successfully')


def reset_lists_on_screen_city():
    global w
    global top_level

    w.Listbox2.destroy()
    w.string_var_city = tk.StringVar()
    w.string_var_city.set("Select a city")
    w.Listbox2 = tk.OptionMenu(top_level, w.string_var_city, *["Select a city"])
    w.Listbox2.place(relx=0.68, rely=0.556, relheight=0.05, relwidth=0.25)
    w.Listbox2.configure(background="white")
    w.Listbox2.configure(disabledforeground="#a3a3a3")
    w.Listbox2.configure(font="TkFixedFont")
    w.Listbox2.configure(foreground="#000000")
    w.Listbox2.configure(highlightbackground="#d9d9d9")
    w.Listbox2.configure(highlightcolor="black")
    w.Listbox2.configure(width=10)


def reset_lists_on_screen_query():
    global w
    global top_level

    w.Listbox3.destroy()
    w.string_var_query = tk.StringVar()
    w.string_var_query.set("Select a query number")
    w.Listbox3 = tk.OptionMenu(top_level, w.string_var_query, *["Select a query number"])
    w.Listbox3.place(relx=0.4, rely=0.885, relheight=0.05, relwidth=0.35)
    w.Listbox3.configure(background="white")
    w.Listbox3.configure(disabledforeground="#a3a3a3")
    w.Listbox3.configure(font="TkFixedFont")
    w.Listbox3.configure(foreground="#000000")
    w.Listbox3.configure(highlightbackground="#d9d9d9")
    w.Listbox3.configure(highlightcolor="black")
    w.Listbox3.configure(width=10)


def reset_lists_on_screen_language():
    global w
    global top_level

    w.Listbox1.destroy()
    w.string_var_language = tk.StringVar()
    w.string_var_language.set("Select a language")
    w.Listbox1 = tk.OptionMenu(top_level, w.string_var_language, *["Select a language"])
    w.Listbox1.place(relx=0.35, rely=0.556, relheight=0.05, relwidth=0.3)
    w.Listbox1.configure(background="white")
    w.Listbox1.configure(disabledforeground="#a3a3a3")
    w.Listbox1.configure(font="TkFixedFont")
    w.Listbox1.configure(foreground="#000000")
    w.Listbox1.configure(highlightbackground="#d9d9d9")
    w.Listbox1.configure(highlightcolor="black")
    w.Listbox1.configure(width=10)


def showButton():
    global in_process
    global stemmer
    global dist_path

    if not in_process:
        if stemmer:
            file = dist_path + "/term_dictionary_stemmer.pkl"
        else:
            file = dist_path + "/term_dictionary.pkl"
        if dist_path == "":
            showwarning('Warning', 'Please insert Path to save files.')
        elif dist_path == "" or not os.path.isfile(file):
            showwarning('Warning', 'Terms dictionary is not exists.')
        else:
            def show():
                if stemmer:
                    file = open(dist_path + "/term_dictionary_stemmer.pkl", "rb+")
                else:
                    file = open(dist_path + "/term_dictionary.pkl", "rb+")
                term_dictionary_to_show = pickle.load(file)
                file.close()
                toplevel = tk.Toplevel()
                toplevel.title('Term dictionary')
                toplevel.geometry('400x400')
                toplevel.resizable(False, False)
                scrollbar = tk.Scrollbar(toplevel)
                scrollbar.pack(side='right', fill='y')
                treeview = ttk.Treeview(toplevel, yscrollcommand = scrollbar.set, show="tree")
                treeview.pack(fill="both", expand=True)
                treeview['show'] = 'headings'
                treeview['columns'] = ('Term', 'Frequency')
                treeview.column('Term', anchor=tk.CENTER)
                treeview.column('Frequency', anchor=tk.CENTER)
                treeview.heading('Term', text='Term')
                treeview.heading('Frequency', text='Frequency')
                for term in term_dictionary_to_show:
                    treeview.insert('', 'end', text='Term', values=(str(term), str(term_dictionary_to_show[term][0])))
                treeview.pack(side='left', fill = 'both')
                scrollbar.config(command = treeview.yview())

            t = threading.Thread(target=show())
            t.start()
            showinfo('info', 'Starts uploading the dictionary')


def show_res():
    global w
    global in_process
    global query_res

    key = w.string_var_query.get()
    if not in_process:
        if key == "Select a query number":
            showwarning('Warning', 'Please select query number.')
        else:
            toplevel = tk.Toplevel()
            toplevel.title(key)
            toplevel.geometry('650x300')
            toplevel.resizable(False, False)
            scrollbar = tk.Scrollbar(toplevel)
            scrollbar.pack(side='right', fill='y')
            treeview = ttk.Treeview(toplevel, yscrollcommand = scrollbar.set, show="tree")
            treeview.place(height=100, width=50)
            treeview['show'] = 'headings'
            treeview['columns'] = ('Serial Number', 'Document Name')
            treeview.column('Serial Number', anchor=tk.CENTER)
            treeview.column('Document Name', anchor=tk.CENTER)
            treeview.heading('Serial Number', text='Serial Number')
            treeview.heading('Document Name', text='Document Name')
            treeview.pack(side='left', fill='both')
            scrollbar.config(command=treeview.yview())

            index = 1
            doc_list = []
            for doc_num in query_res[key]:
                treeview.insert('', 'end', text='Term', values=(str(index), doc_num[0]))
                doc_list.append(doc_num[0])
                index += 1

            string_doc = tk.StringVar()
            string_doc.set("Select a Document")
            option_menu = tk.OptionMenu(toplevel, string_doc, *doc_list)
            option_menu.place(relx=0.64, rely=0.241, relheight=0.1, relwidth=0.32)
            option_menu.configure(background="white")
            option_menu.configure(disabledforeground="#a3a3a3")
            option_menu.configure(font="TkFixedFont")
            option_menu.configure(foreground="#000000")
            option_menu.configure(highlightbackground="#d9d9d9")
            option_menu.configure(highlightcolor="black")
            option_menu.configure(width=10)

            list = tk.Listbox(toplevel)
            list.place(relx=0.72, rely=0.49, height=80, width=100)

            get = tk.Button(toplevel)
            get.place(relx=0.75, rely=0.38, height=24, width=49)
            get.configure(activebackground="#ececec")
            get.configure(activeforeground="#000000")
            get.configure(background="#d9d9d9")
            get.configure(disabledforeground="#a3a3a3")
            get.configure(foreground="#000000")
            get.configure(highlightbackground="#d9d9d9")
            get.configure(highlightcolor="black")
            get.configure(pady="0")
            get.configure(text='''Get''')
            get.bind('<Button-1>', lambda e: get_key_entities(string_doc, list))

            save_btn = tk.Button(toplevel)
            save_btn.place(relx=0.75, rely=0.8, height=24, width=49)
            save_btn.configure(activebackground="#ececec")
            save_btn.configure(activeforeground="#000000")
            save_btn.configure(background="#d9d9d9")
            save_btn.configure(disabledforeground="#a3a3a3")
            save_btn.configure(foreground="#000000")
            save_btn.configure(highlightbackground="#d9d9d9")
            save_btn.configure(highlightcolor="black")
            save_btn.configure(pady="0")
            save_btn.configure(text='''Save''')
            save_btn.bind('<Button-1>', lambda e: save_res(key, doc_list))


def save_all():
    global query_res

    if not in_process:
        if len(query_res) == 0:
            showwarning('Warning', 'Please run query.')
        else:
            path = filedialog.askdirectory(title="Choose dir")
            fileName = path + "/queries_res.txt"
            file = open(fileName, "w+")
            res = ""
            for key in query_res:
                doc_list = []
                for doc_num in query_res[key]:
                    doc_list.append(doc_num[0])
                key = key.replace('query_', "")
                for doc in doc_list:
                    res += (str(key) + " 0 " + doc + " 1 " + " 2 mt" + "\n")
            res = res[:-1]
            file.write(res)
            file.close()
            showinfo('info', 'Queries save.')


def save_res(key, doc_list):
    path = filedialog.askdirectory(title="Choose dir")
    res = ""
    fileName = path + "/" + key + ".txt"
    file = open(fileName, "w+")
    key = key.replace('query_', "")
    for doc in doc_list:
        res += (str(key) + " 0 " + doc + " 1 " + " 2 mt" + "\n")
    res = res[:-1]
    file.write(res)
    file.close()
    showinfo('info', 'File save.')


def get_key_entities(string_doc, list):

    def get(string_doc, list):
        global stemmer

        list.delete(0, tk.END)
        doc_num = string_doc.get()
        if not doc_num == "Select a Document":
            if stemmer:
                file = open(dist_path + "/document_dictionary_stemmer.pkl", "rb+")
            else:
                file = open(dist_path + "/document_dictionary.pkl", "rb+")
            document_dictionary = pickle.load(file)
            file.close()
            l = document_dictionary[doc_num].terms_in_doc
            i = 0
            for word in l:
                list.insert(i, word)
                i += 1
    t = threading.Thread(target=get(string_doc, list))
    t.start()
    showinfo('info', 'It will take a few seconds...')


def stemCbox():
    global stemmer
    global in_process
    global term_dictionary_in_corpus

    if not in_process:
        if stemmer == True:
            stemmer = False
        else:
            stemmer = True


def semanticCbox():
    global semantic
    global in_process

    if not in_process:
        if semantic == True:
            semantic = False
        else:
            semantic = True


def uploadButton():
    global in_process
    global dist_path
    global query_res

    if not in_process:
        if stemmer:
            file = dist_path + "/term_dictionary_stemmer.pkl"
        else:
            file = dist_path + "/term_dictionary.pkl"
        if dist_path == "":
            showwarning('Warning', 'Please insert Path to save files.')
        elif dist_path == "" or not os.path.isfile(file):
            showwarning('Warning', 'Terms dictionary is not exists.')
        else:
            def upload():
                global term_dictionary_in_corpus

                if stemmer:
                    file = open(dist_path + "/term_dictionary_stemmer.pkl", "rb+")
                else:
                    file = open(dist_path + "/term_dictionary.pkl", "rb+")
                term_dictionary_in_corpus = pickle.load(file)
                file.close()
                fill_language_list()
                fill_city_list()
                query_res.clear()
                showinfo('info', 'Terms dictionary upload successfully')
                bord_state('normal')
            t = threading.Thread(target=upload)
            t.start()
            bord_state('disable')
            showinfo('info', 'Upload dictionary will take about 1 minute.' + '\r\n' +
                     'When the process is finished the window keys will be released.')


def reset_language():
    global language_choice
    global in_process

    if not in_process:
        language_choice.clear()
        showinfo('info', 'Reset all selected languages.')


def reset_city():
    global city_choice
    global in_process

    if not in_process:
        city_choice.clear()
        showinfo('info', 'Reset all selected citys.')


def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top


def destroy_window():
    # Function which closes the window.
    global top_level
    global in_process

    if not in_process:
        top_level.destroy()
        top_level = None


if __name__ == '__main__':
    import gui
    gui.vp_start_gui()
