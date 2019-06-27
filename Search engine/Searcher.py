import os
import pickle

import Parse
import Ranker


def search(posting_path, query, stemmer, query_source_path, list_of_language, list_of_city, semantic):
    Parse.set_stop_words_file(posting_path + "/stop_words.txt")
    list_save_queries = Parse.parse_queries(query_source_path, posting_path, query, stemmer, semantic)
    res = {}
    for query_post in list_save_queries:
        fileName = posting_path + "/" + query_post + ".pkl"
        file = open(fileName, "rb+")
        querie_term_dictionary = pickle.load(file)
        file.close()
        os.remove(fileName)
        query_name = query_post.replace('post', "")
        res[query_name] = Ranker.rank(posting_path, stemmer, querie_term_dictionary, list_of_language, list_of_city)
    return res
