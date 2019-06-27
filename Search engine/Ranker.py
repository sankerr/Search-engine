import operator
import pickle
from math import log2, sqrt

mini_posting = {}
documents_not_with_rank = {}
documents_with_rank = {}
folder_path = ''
stem_mode = False
average_document_length = 0
number_of_documents = 0
bm25_weight = 0
cos_sim_weight = 0
bm25_k = 0  # Range: [1.2 - 2.0]
bm25_b = 0  # Range: 0-1.0
bm25_idf = 0 # Range: 0-1.0

def reset():
    global mini_posting
    global documents_not_with_rank
    global documents_with_rank
    global folder_path
    global stem_mode
    global average_document_length
    global number_of_documents
    global bm25_weight
    global cos_sim_weight
    global bm25_k
    global bm25_b
    global bm25_idf

    mini_posting = {}
    documents_not_with_rank = {}
    documents_with_rank = {}
    folder_path = ''
    stem_mode = False
    average_document_length = 0
    number_of_documents = 0
    bm25_weight = 0
    cos_sim_weight = 0
    bm25_k = 0
    bm25_b = 0
    bm25_idf = 0

def set_folder_path(folder_path_to_save):
    global folder_path

    folder_path = folder_path_to_save


def set_average_document_length():
    global stem_mode
    global folder_path
    global average_document_length
    global number_of_documents

    if stem_mode:
        file = open(folder_path + "/document_dictionary_stemmer" + ".pkl", "rb+")
        document_dic = pickle.load(file)
        file.close()
    else:
        file = open(folder_path + "/document_dictionary" + ".pkl", "rb+")
        document_dic = pickle.load(file)
        file.close()
    sum = 0
    number_of_documents = len(document_dic)
    for document in document_dic:
        sum += document_dic[document].length
    average_document_length = sum / number_of_documents


def set_stem_mode(stem_mode_to_save):
    global stem_mode
    global bm25_b
    global bm25_weight
    global cos_sim_weight
    global bm25_k
    global bm25_idf

    stem_mode = stem_mode_to_save
    set_average_document_length()
    bm25_weight = 0.7
    cos_sim_weight = 0.3
    bm25_k = 1.2  # Range: [1.2 - 2.0]
    bm25_b = 0.75  # Range: 0-1.0
    bm25_idf = 0.5  # Range: 0-1.0


def create_mini_posting(querie_term_dictionary):
    global folder_path
    global stem_mode

    if stem_mode:
        file = open(folder_path + "/term_dictionary_stemmer.pkl", "rb+")
        term_dictionary = pickle.load(file)
        file.close()
    else:
        file = open(folder_path + "/term_dictionary.pkl", "rb+")
        term_dictionary = pickle.load(file)
        file.close()
    for term in querie_term_dictionary:
        if term.upper() in term_dictionary:
            term = term.upper()
        if term in term_dictionary:
            file = open(term_dictionary[term][1], "rb+")
            posting = pickle.load(file)
            file.close()
        else:
            continue
        term_post = posting[term]
        mini_posting[term] = term_post


def create_document_dictionary(list_of_language, list_of_city):
    global stem_mode
    global folder_path
    global mini_posting
    global documents_not_with_rank

    if stem_mode:
        file = open(folder_path + "/document_dictionary_stemmer" + ".pkl", "rb+")
        document_dic = pickle.load(file)
        file.close()
        file = open(folder_path + "/city_dictionary_stemmer" + ".pkl", "rb+")
        dic_city = pickle.load(file)
        file.close()
    else:
        file = open(folder_path + "/document_dictionary" + ".pkl", "rb+")
        document_dic = pickle.load(file)
        file.close()
        file = open(folder_path + "/city_dictionary" + ".pkl", "rb+")
        dic_city = pickle.load(file)
        file.close()
    if len(list_of_city) == 0:
        need_check_city = False
    else:
        need_check_city = True
    if len(list_of_language) == 0:
        need_check_language = False
    else:
        need_check_language = True
    for line in mini_posting:
        for doc in mini_posting[line].frequencyInDoc:
            if not doc in documents_not_with_rank:
                legal = True
                if need_check_language:
                    legal = check_language(doc, document_dic, list_of_language)
                if legal and need_check_city:
                    legal = check_city(doc, document_dic, list_of_city, dic_city)
                if legal:
                    documents_not_with_rank[doc] = document_dic[doc]


def check_language(doc_num, document_dic, list_of_language):
    language = document_dic[doc_num].language
    if language in list_of_language:
        return True
    else:
        return False


def check_city(doc_num, document_dic, list_of_city, dic_city):
    city = document_dic[doc_num].city
    if city in list_of_city:
        return True
    if in_text(doc_num, dic_city, list_of_city):
        return True
    return False


def in_text(doc_num, dic_city, list_of_city):
    for city in list_of_city:
        city = city.lower()
        doc_list = dic_city[city][1]
        if doc_num in doc_list:
            return True
    return False


def calc_bm_25():
    global documents_not_with_rank
    global mini_posting
    global bm25_idf
    global bm25_k
    global bm25_b
    global average_document_length
    global documents_with_rank
    global bm25_weight
    global number_of_documents

    for doc in documents_not_with_rank:
        document_length = documents_not_with_rank[doc].length
        bm_25_value = 0
        for term in mini_posting:
            if doc not in mini_posting[term].frequencyInDoc:
                continue
            nq = mini_posting[term].df
            value_for_idf = (number_of_documents - nq + bm25_idf) / (nq + bm25_idf)
            idf = float(log2(value_for_idf))
            f_query_doc = mini_posting[term].frequencyInDoc[doc] #/ documents_not_with_rank[doc].maxTf  # tf / max_tf
            numerator = idf * (f_query_doc * (bm25_k + 1))
            denominator = (f_query_doc + bm25_k * (1 - bm25_b + (bm25_b * document_length / average_document_length)))
            bm_25_value += (numerator / denominator)
        documents_with_rank[doc] = bm25_weight * bm_25_value


def calc_sim(querie_term_dictionary):
    global mini_posting
    global documents_not_with_rank
    global cos_sim_weight
    global number_of_documents

    denominator_2 = 0
    for term in mini_posting:
        wq = querie_term_dictionary[term.lower()].term_rank
        denominator_2 += pow(wq, 2)
    denominator_2 = sqrt(denominator_2)

    for doc in documents_not_with_rank:
        numerator = 0
        denominator_1 = 0
        for term in mini_posting:
            if doc not in mini_posting[term].frequencyInDoc:
                continue
            idf = log2(number_of_documents / mini_posting[term].df)
            tf = mini_posting[term].frequencyInDoc[doc] / documents_not_with_rank[doc].maxTf
            w = idf * tf
            wq = querie_term_dictionary[term.lower()].term_rank
            numerator += (w * wq)
            denominator_1 += pow(w, 2)
        denominator = sqrt(denominator_1) * denominator_2
        cosine_value = numerator / denominator
        documents_with_rank[doc] += (cos_sim_weight * cosine_value)


def sort_res():
    global documents_with_rank

    res = []
    documents_with_rank = sorted(documents_with_rank.items(), key=operator.itemgetter(1))
    size = len(documents_with_rank) - 1
    lim = size + 1
    if lim > 50:
        lim = 50
    for i in range(0, lim):
        res.append(documents_with_rank[size - i])
    return res


def rank(folder_path, stem_mode, querie_term_dictionary, list_of_language, list_of_city):
    reset()
    set_folder_path(folder_path)
    set_stem_mode(stem_mode)
    create_mini_posting(querie_term_dictionary)
    create_document_dictionary(list_of_language, list_of_city)
    calc_bm_25()
    calc_sim(querie_term_dictionary)
    return sort_res()
