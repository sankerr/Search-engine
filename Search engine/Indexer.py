# Indexer class
# That class menage the all process of the system
# That class responsible of pass the path to the read file that read the corpus.
# And to merge the output of the parse class.
# Merge the document dictionaries and the posting file.

import datetime
import os
import pickle
import operator

import Parse
import ReadFile
from TmpPost import TmpPost

# The main func receive the paths and empty dictionary and boolean if to stemming
def start_read(corpus_path, posting_path, term_dictionary, stemmer):
    Parse.set_stop_words_file(corpus_path + "/stop_words.txt")
    Parse.copy_stop_words_file(corpus_path + "/stop_words.txt", posting_path + "/stop_words.txt")
    directory_corpus = os.fsdecode(corpus_path)
    sub_dir_list = os.listdir(directory_corpus)
    size = int((len(sub_dir_list)-1) / 10)  # read the corpus in 11 parts
    if size == 0:
        size = 10
    idx = 1
    counter = 1
    ReadFile.__reset()
    ReadFile.creat_world_city_dictionary()
    for dir in sub_dir_list:
        if not dir == "stop_words.txt":
            ReadFile.creat_corpus_city_dictionary(corpus_path, dir)
    corpus_city_dictionary = {}
    city_dic = ReadFile.corpus_city_dictionary
    city_list = sorted(city_dic)
    for key in city_list:
        corpus_city_dictionary[key] = [city_dic[key], {}]
    ReadFile.__reset()
    sub_dir_list = os.listdir(directory_corpus)
    for dir in sub_dir_list:
        if not dir == "stop_words.txt":
            if counter % size == 0:
                docDict = ReadFile.docDictionary
                Parse.parse_docs({}, term_dictionary, corpus_city_dictionary, ReadFile.textDic, docDict, idx, stemmer, posting_path)
                time = datetime.datetime.now()
                ReadFile.__reset()
                idx += 1
            ReadFile.split_doc(corpus_path, dir)
            counter += 1
    if not counter % size == 0:
        Parse.parse_docs({}, term_dictionary, corpus_city_dictionary, ReadFile.textDic, ReadFile.docDictionary, idx, stemmer, posting_path)
        ReadFile.__reset()
    if stemmer:
        file = open(posting_path + "/city_dictionary_stemmer" + ".pkl", "wb+")
    else:
        file = open(posting_path + "/city_dictionary" + ".pkl", "wb+")
    pickle.dump(corpus_city_dictionary, file, pickle.HIGHEST_PROTOCOL)
    file.close()
    return idx


# Func that merge the different document dictionaries
def merge_document_dictionary(Document_Dictionary, num_of_post, stemmer):
    merg_doc_dict = {}
    for i in range (1, num_of_post+1):
        fileName = Document_Dictionary + "/doc" + str(i) + ".pkl"
        file = open(fileName, "rb+")
        dic = pickle.load(file)
        file.close()
        os.remove(fileName)
        for key in dic:
            merg_doc_dict[key] = dic[key]
    if stemmer:
        file = open(Document_Dictionary + "/document_dictionary_stemmer" + ".pkl", "wb+")
    else:
        file = open(Document_Dictionary + "/document_dictionary" + ".pkl", "wb+")
    pickle.dump(merg_doc_dict, file, pickle.HIGHEST_PROTOCOL)
    file.close()
    return len(merg_doc_dict)

# The func that merge all the tmp posting files
# The func receive the path the term dictionary the number f posting files and stemming
def new_merge(posting_path, term_dictionary, num_of_post, stemmer):
    not_finish = True
    tmp_post = []  # tmp posting file list
    for i in range (1, num_of_post+1):
        # add to the list the 10,000 terms from each posting file
        tmp_post.append(create_tmp_post(posting_path, i, 0, term_dictionary))
    terms = []  # list of the first term from each tmp post
    for tmp in tmp_post:
        terms.append([tmp.keys[0], tmp])  # add the first terms and the tmp post that it came from
    posting_index = 1
    term_counter = 0
    if stemmer:
        posting_name = "final_posting_stemmer" + str(posting_index)
    else:
        posting_name = "final_posting" + str(posting_index)
    final_posting = {}
    while not_finish:
        terms = sorted(terms, key=operator.itemgetter(0))  # sorting by the key
        key = terms[0][0]
        value = terms[0][1].dictionary[key]
        final_term = [key, value]
        del terms[0][1].dictionary[key]  # delete the element from the tmp post
        del terms[0][1].keys[0]
        for index in range(0, num_of_post):  # search in the list for identical terms
            try:
                if terms[0][0] == terms[1][0]:
                    key = terms[1][0]
                    final_term = merge_final_term(final_term, terms[1][1].dictionary[key])
                    del terms[1][1].dictionary[key]  # delete the element from the dicitionary
                    del terms[1][1].keys[0]  # delete the element from the keys array
                    if len(terms[1][1].dictionary) == 0:
                        terms[1][1] = create_tmp_post(posting_path, terms[1][1].post_num, terms[1][1].num_of_update, term_dictionary)
                    if not len(terms[1][1].dictionary) == 0:
                        terms.append([terms[1][1].keys[0], terms[1][1]])
                    del terms[1]
                    if len(terms) == 1:
                        not_finish = False
                        break
                else:
                    break
            except:
                print()
        if len(terms[0][1].dictionary) == 0:  # check if the tmp post is empty
            terms[0][1] = create_tmp_post(posting_path, terms[0][1].post_num, terms[0][1].num_of_update, term_dictionary)  # add the next N terms from the posting file
        if not len(terms[0][1].dictionary) == 0:  # check if after loading element from posting there are element in the tmp posting
            terms.append([terms[0][1].keys[0], terms[0][1]])  # add the next element from the tmp post
        if len(terms) < 3:  # 2 cause in the next line we delete the first one
            not_finish = False
        del terms[0]  # delete the first term from the terms array
        term_dictionary[key][1] = posting_path + "/" + posting_name + ".pkl"
        final_posting[final_term[0]] = final_term[1]
        term_counter += 1
        if term_counter == 40000:
            term_counter = 0
            file = open(posting_path + "/" + posting_name + ".pkl", "wb+")
            pickle.dump(final_posting, file, pickle.HIGHEST_PROTOCOL)
            file.close()
            final_posting.clear()
            posting_index += 1
            if stemmer:
                posting_name = "final_posting_stemmer" + str(posting_index)
            else:
                posting_name = "final_posting" + str(posting_index)
    if len(terms[0][1].dictionary) == 0:  # check if the tmp post is empty
        terms[0][1] = create_tmp_post(posting_path, terms[0][1].post_num, terms[0][1].num_of_update, term_dictionary)
    size = len(terms[0][1].keys)
    while(size>0):
        key = terms[0][1].keys[0]
        value = terms[0][1].dictionary[key]
        final_posting[key] = value
        if len(terms[0][1].dictionary) == 0:  # check if the tmp post is empty
            terms[0][1] = create_tmp_post(posting_path,terms[0][1].post_num, terms[0][1].num_of_update, term_dictionary)
        del terms[0][1].dictionary[key]  # delete the element from the tmp post
        del terms[0][1].keys[0]
        term_dictionary[key][1] = posting_path + "/" + posting_name + ".pkl"
        term_counter += 1
        if term_counter == 40000:
            term_counter = 0
            file = open(posting_path + "/" + posting_name + ".pkl", "wb+")
            pickle.dump(final_posting, file, pickle.HIGHEST_PROTOCOL)
            file.close()
            final_posting.clear()
            posting_index += 1
            if stemmer:
                posting_name = "final_posting_stemmer" + str(posting_index)
            else:
                posting_name = "final_posting" + str(posting_index)
        size = len(terms[0][1].keys)
    if len(final_posting) > 0:
        file = open(posting_path + "/" + posting_name + ".pkl", "wb+")
        pickle.dump(final_posting, file, pickle.HIGHEST_PROTOCOL)
        file.close()
    for i in range (1, num_of_post+1):
        os.remove(posting_path + "/post" + str(i) + ".pkl")

# Func that ceate the tmp posting and insert 10,000 terms
def create_tmp_post(posting_path, post_num, num_of_update, term_dictionary):
    file_name = posting_path + "/post" + str(post_num)+".pkl"
    file = open(file_name, "rb")
    tmp = pickle.load(file)
    file.close()
    term_num = num_of_update * 10000
    tmp_pos = TmpPost(post_num, {}, [], num_of_update)
    x = 1
    for key in tmp:
        upper_key = key.upper()
        if x > term_num:  # number of element we ara already read
            if key in term_dictionary:
                tmp_pos.keys.append(key)
                tmp_pos.dictionary[key] = tmp[key]
            elif upper_key in term_dictionary:
                tmp_pos.keys.append(upper_key)
                tmp_pos.dictionary[upper_key] = tmp[key]
        if x > term_num and x % 10000 == 0:  # 1000 element or all the element in the file
            break
        x += 1
    tmp_pos.num_of_update += 1
    return tmp_pos


def merge_final_term(final_term, value):
    final_term[1].df += value.df
    for key in value.frequencyInDoc:
        final_term[1].frequencyInDoc[key] = value.frequencyInDoc[key]
    return final_term


def extract_entity(term_dictionary, dist_path, num_of_post):
    for index in range(1, num_of_post + 1):
        file_name = dist_path + "/doc" + str(index) + ".pkl"
        file = open(file_name, "rb")
        tmp = pickle.load(file)
        file.close()
        for key in tmp:
            terms = tmp[key].terms_in_doc
            upper_terms_in_doc = {}
            for term in terms:
                if term.isalpha() and term.upper() in term_dictionary:
                    upper_terms_in_doc[term.upper()] = terms[term]
            # sort the terms by there frequency
            upper_terms_in_doc = sorted(upper_terms_in_doc.items(), key=operator.itemgetter(1))
            size = len(upper_terms_in_doc) - 1
            final_terms = {}
            # take the first 5 elements from the dictionary
            for num in range(0, min(5, size+1)):
                final_terms[upper_terms_in_doc[size-num][0]] = upper_terms_in_doc[size-num][1]
            tmp[key].terms_in_doc = final_terms
        file2 = open(dist_path + "/doc" + str(index) + ".pkl", "wb+")
        pickle.dump(tmp, file2, pickle.HIGHEST_PROTOCOL)
        file.close()


if __name__ == '__main__':
    global stemmer
    global dist_path
    global corpus_path

    total = datetime.datetime.now()
    term_dictionary = {}
    num_of_post = start_read(corpus_path, dist_path, term_dictionary, stemmer)
    extract_entity(term_dictionary, dist_path, num_of_post)
    num_of_doc = merge_document_dictionary(dist_path, num_of_post, stemmer)
    new_merge(dist_path, term_dictionary, num_of_post, stemmer)
    sort_key = sorted(term_dictionary)
    sort_term_dictionary = {}
    for key in sort_key:
        sort_term_dictionary[key] = term_dictionary[key]
    if stemmer:
        file = open(dist_path + "/term_dictionary_stemmer.pkl", "wb+")
    else:
        file = open(dist_path + "/term_dictionary.pkl", "wb+")
    pickle.dump(sort_term_dictionary, file, pickle.HIGHEST_PROTOCOL)
    file.close()
    num_of_terms = len(sort_term_dictionary)
    total_time = "Total time: " + str(datetime.datetime.now() - total)
