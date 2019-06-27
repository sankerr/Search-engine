# Class Parse
# That class
import json
import pickle
import re
from shutil import copyfile
from urllib.request import urlopen

from MetaData import MetaData
from PorterStemmer import PorterStemmer

__months_dictionary = {'january': '01', 'jan': '01', 'february': '02', 'feb': '02', 'march': '03',
                       'mar': '03','april': '04', 'apr': '04', 'may': '05', 'june': '06', 'jun': '06',
                       'july': '07','jul': '07','august': '08', 'aug': '08', 'september': '09',
                       'sep': '09', 'october': '10', 'oct': '10','november': '11', 'nov': '11',
                       'december': '12', 'dec': '12'}
__months_set = {'january', 'jan', 'february', 'feb', 'march', 'mar', 'april', 'apr',
                'may', 'june', 'jun', 'july', 'jul', 'august', 'aug', 'september',
                'sep', 'october', 'oct', 'november', 'nov', 'december', 'dec'}
__punctuations_set = {'[', '(', '{', '`', ')', '<', '|', '&', '~', '+', '^', '@', '*', '?', '.',
                      '>', ';', '_', '\'', ':', ']', '/', '\\', "}", '!', '=', '#', ',', '\"', '-'}
__stop_words = ''
__stemmer = False
stemmer_dictionary = {}

# setter of the stemmer
def set_stemmer(val):
    global __stemmer
    __stemmer = val

# setter of the stop word list
def set_stop_words_file(path):
    global __stop_words

    with open(path) as wordbook:
        __stop_words = set(word.strip() for word in wordbook)


def copy_stop_words_file(path, posting_path):
    try:
        with open(path) as wordbook:
            copyfile(path, posting_path)
            wordbook.close()
    except:
        wordbook.close()


def __clean_token(token):
    token_length = len(token)
    while (token_length > 0) and token[0] in __punctuations_set:
        token = token[1:]
        token_length -= 1

    while (token_length > 1) and token[token_length - 1] in __punctuations_set:
        token = token[:-1]
        token_length -= 1

    return token

# check if the strinf in a number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# check if the word is only char and not in the stop word list
def __is_valid_word(token, token_lower):
    return token.isalpha() and token_lower not in __stop_words and not token == ""

# check if its a valid number
def __is_valid_number(token):
    percent_symbol_flag = False
    fraction_flag = False
    number_of_dots = 0
    token = token.replace("$", "")
    if len(token) == 0:
        return False

    two_last_char = token[-2:]
    one_last_char = two_last_char[-1:]

    if two_last_char == "bn" or one_last_char == "m":
        if two_last_char == "bn":
            token = token[:-2]
        else:
            token = token[:-1]
        for c in token:
            is_numeric_number = c.isnumeric()
            is_punctuation = False
            if c == '.' or c == ',' or c == '%' or c == '/':
                is_punctuation = True
                if c == '.':
                    number_of_dots += 1
            if (not is_numeric_number) and (not is_punctuation):
                return False

        if number_of_dots > 1:
            return False
        else:
            return True

    else:
        if token == '%':
            return False
        for c in token:
            if c == '%':
                percent_symbol_flag = True
                if token == '%':
                    return False
            elif c == '/':
                fraction_flag = True
            is_numeric_number = c.isnumeric()
            is_punctuation = False
            if c == '.' or c == ',' or c == '%' or c == '/':
                is_punctuation = True
                if c == '.':
                    number_of_dots += 1
            if (not is_numeric_number) and (not is_punctuation):
                return False

        if number_of_dots > 1:
            return False
        if percent_symbol_flag:
            i = 0
            while i < (len(token) - 1):
                if token[i] == '%':
                    return False
                i += 1

        if fraction_flag:
            fraction_list = token.split('/')
            if not fraction_list[1].isnumeric():
                return False
            if len(fraction_list) != 2:
                return False

    return True

# check if its a valid date by the formats
def __is_valid_date(text, token_lower, next_token_lower, index, index_last_token):
    ans = False

    # the token is a month, for example: May, June
    if token_lower in __months_set and index + 2 < index_last_token + 1 and token_lower.isnumeric() \
            and 0 < int(token_lower) <= 31 and next_token_lower in __months_set \
            and (__clean_token(text[index + 2])).isnumeric() \
            and 0 < int(__clean_token(text[index + 2])) < 2800:
        ans = True

    # case 3.1: the token is a number and the next token is a month, for example: 13 May, 4 June
    elif token_lower.isnumeric() and 0 < int(token_lower) <= 31 and next_token_lower in __months_set:
        ans = True

    # case 3.2: the token is a number and the next token is a month, for example: 1988 May, 88 June
    elif token_lower.isnumeric() and 0 < int(token_lower) <= 2800 \
            and next_token_lower in __months_set:
        ans = True

    elif '.' in token_lower and len(token_lower.split(".")) == 3:
        date_token = token_lower.split(".")
        day = date_token[0]
        months = date_token[1]
        year = date_token[2]
        if day.isnumeric() and months.isnumeric() and year.isnumeric():
            ans = True

    return ans


def __insert_dates(posting, term_dictionary, day, month, year, doc_num, docDictionary, terms_in_doc):
    if not month.isnumeric():
        month = __months_dictionary[month]
    day_length = len(day)
    year_length = len(year)

    if year_length != 0 and day_length != 0:
        if 0 < int(year) < 100:
            year = "19" + year
        if day_length == 1:
            day = "0" + day
        term = year + "-" + month + "-" + day
        if term in term_dictionary:
            term_dictionary[term][0] += 1
        else:
            term_dictionary[term] = []
            term_dictionary[term].append(1)
            term_dictionary[term].append("")
        __insert_to_dictionary(posting, term, doc_num, docDictionary, terms_in_doc)
    elif year_length != 0:
        if 0 < int(year) < 100:
            year = "19" + year
        term = year + "-" + month
        if term in term_dictionary:
            term_dictionary[term][0] += 1
        else:
            term_dictionary[term] = []
            term_dictionary[term].append(1)
            term_dictionary[term].append("")
        __insert_to_dictionary(posting, term, doc_num, docDictionary, terms_in_doc)

    elif day_length != 0:
        if day_length == 1:
            day = "0" + day
        term = month + "-" + day
        if term in term_dictionary:
            term_dictionary[term][0] += 1
        else:
            term_dictionary[term] = []
            term_dictionary[term].append(1)
            term_dictionary[term].append("")
        __insert_to_dictionary(posting, term, doc_num, docDictionary, terms_in_doc)
    pass


def __insert_to_dictionary(posting, token, docNum, docDictionary, terms_in_doc):
    if token in terms_in_doc:
        terms_in_doc[token] += 1
    else:
        terms_in_doc[token] = 1
    if token in posting:
        if docNum in posting[token].frequencyInDoc:
            curTf = posting[token].frequencyInDoc[docNum] + 1
            posting[token].frequencyInDoc[docNum] = curTf
            if not len(docDictionary) == 0 and docDictionary[docNum].maxTf < curTf:
                docDictionary[docNum].maxTf = curTf
        else:
            curDf = posting[token].df
            posting[token].df = curDf + 1
            posting[token].frequencyInDoc[docNum] = 1
    else:
        frequencyInDoc = {}
        frequencyInDoc[docNum] = 1
        posting[token] = MetaData(1, frequencyInDoc)


def parse_text(posting, term_dictionary, corpus_city_dictionary, text, doc_num, docDictionary, stemmer):
    terms_in_doc = {}
    ps = PorterStemmer()
    text = text.split()
    index = 0
    index_last_token = len(text) - 1
    while index < index_last_token + 1:
        token = __clean_token(text[index])
        token_length = len(token)
        if token_length > 0:  # check if the token not empty
            if token[0].isdigit():
                if token_length > 2 and token[-2:] == "th":
                    token = token[:-2]
                    token_length = len(token)
                elif ")" in token:
                    tmp = token.split(")")
                    token = tmp[len(tmp)-1]
            token_lower = token.lower()
            token_upper = token.upper()
            next_token = ""
            next_token_lower = ""
            if index < index_last_token:
                next_token = __clean_token(text[index + 1])
                next_token_lower = next_token.lower()

            # case 1: - or between
            if '-' in token or token == "between" or token == "Between":
                if '--' in token:  # invalid token, 2 '-'
                    index += 1
                    continue
                elif (token == "between" or token == "Between") and index + 3 < index_last_token:
                    first_num = __clean_token(text[index + 1])
                    second_num = __clean_token(text[index + 3])
                    if first_num.isnumeric() and second_num.isnumeric():
                        token = first_num + "-" + second_num
                token_split = token.split("-")

                # case 1.1: word-num or num-word
                if len(token_split) > 1:
                    if (token_split[0].isalpha() and is_number(token_split[1])) or \
                            (token_split[1].isalpha() and is_number(token_split[0])):
                        token = token_split[0] + "-" + token_split[1]
                        if token_lower in term_dictionary:
                            term_dictionary[token_lower][0] += 1
                        else:
                            term_dictionary[token_lower] = []
                            term_dictionary[token_lower].append(1)
                            term_dictionary[token_lower].append("")
                        __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)

                    # case 1.2: word-word or word-word-word
                    elif token_split[0].isalpha():
                        only_words = True
                        for word in token_split:
                            if not word.isalpha():
                                only_words = False
                        if only_words:
                            if token_lower in term_dictionary:
                                term_dictionary[token_lower][0] += 1
                            else:
                                term_dictionary[token_lower] = []
                                term_dictionary[token_lower].append(1)
                                term_dictionary[token_lower].append("")
                            __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)

                            for x in range(0, len(token_split)):  # insert every word
                                token = token_split[x]
                                token_lower = token.lower()
                                token_upper = token.upper()
                                if token_lower in __stop_words:
                                    index += 1
                                    continue
                                if token_lower in corpus_city_dictionary:
                                    if doc_num in corpus_city_dictionary[token_lower][1]:
                                        corpus_city_dictionary[token_lower][1][doc_num].append(index)
                                    else:
                                        corpus_city_dictionary[token_lower][1][doc_num] = [index]
                                if token[0].isupper():
                                    if token.isupper():
                                        if (stemmer):
                                            if token_lower not in stemmer_dictionary:
                                                tmp = token_lower
                                                token_lower = ps.stem(token_lower)
                                                token_upper = token_lower.upper()
                                                stemmer_dictionary[tmp] = token_lower
                                            else:
                                                token_lower = stemmer_dictionary[token_lower]
                                                token_upper = token_lower.upper()
                                        if token_upper in term_dictionary:
                                            term_dictionary[token_upper][0] += 1
                                            __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                                        elif token_lower in term_dictionary:
                                            term_dictionary[token_lower][0] += 1
                                            __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                                        else:
                                            term_dictionary[token_upper.lower()] = []
                                            term_dictionary[token_upper.lower()].append(1)
                                            term_dictionary[token_upper.lower()].append("")
                                            __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                                    else:
                                        if (stemmer):
                                            if token_lower not in stemmer_dictionary:
                                                tmp = token_lower
                                                token_lower = ps.stem(token_lower)
                                                token_upper = token_lower.upper()
                                                stemmer_dictionary[tmp] = token_lower
                                            else:
                                                token_lower = stemmer_dictionary[token_lower]
                                                token_upper = token_lower.upper()
                                        if token_upper in term_dictionary:
                                            term_dictionary[token_upper][0] += 1
                                            __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                                        elif token_lower in term_dictionary:
                                            term_dictionary[token_lower][0] += 1
                                            __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                                        else:
                                            term_dictionary[token_upper] = []
                                            term_dictionary[token_upper].append(1)
                                            term_dictionary[token_upper].append("")
                                            __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                                else:
                                    if (stemmer):
                                        if token_lower not in stemmer_dictionary:
                                            tmp = token_lower
                                            token_lower = ps.stem(token_lower)
                                            token_upper = token_lower.upper()
                                            stemmer_dictionary[tmp] = token_lower
                                        else:
                                            token_lower = stemmer_dictionary[token_lower]
                                            token_upper = token_lower.upper()
                                    if token_lower in term_dictionary:
                                        term_dictionary[token_lower][0] += 1
                                        __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                                    elif token_upper in term_dictionary:
                                        term_dictionary[token_lower] = term_dictionary[token_upper]
                                        term_dictionary[token_lower][0] += 1
                                        del term_dictionary[token_upper]
                                        __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                                    else:
                                        term_dictionary[token_lower] = []
                                        term_dictionary[token_lower].append(1)
                                        term_dictionary[token_lower].append("")
                                        __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)

                    # case 1.3: num-num or num-num-num
                    elif is_number(token_split[0]):
                        only_numeric = True
                        for word in token_split:
                            if not is_number(word):
                                only_numeric = False
                        if only_numeric:

                            # case 1.3.1: num-num
                            if len(token_split) == 2:

                                # case 1.3.1.1 Number-number and month (for example: 6-7 July)
                                if next_token_lower in __months_set:
                                    __insert_dates(posting, term_dictionary, token_split[0], next_token_lower, "" ,
                                                   doc_num, docDictionary, terms_in_doc)
                                    __insert_dates(posting, term_dictionary, token_split[1], next_token_lower, "",
                                                   doc_num, docDictionary, terms_in_doc)
                                    index += 1
                                # case 1.3.1.2 regular num-num
                                elif token in term_dictionary:
                                    term_dictionary[token][0] += 1
                                    term_dictionary[token_split[0]][0] += 1
                                    term_dictionary[token_split[1]][0] += 1
                                    __insert_to_dictionary(posting, token, doc_num, docDictionary, terms_in_doc)
                                    __insert_to_dictionary(posting, token_split[0], doc_num, docDictionary, terms_in_doc)
                                    __insert_to_dictionary(posting, token_split[1], doc_num, docDictionary, terms_in_doc)
                                else:
                                    term_dictionary[token] = []
                                    term_dictionary[token].append(1)
                                    term_dictionary[token].append("")
                                    __insert_to_dictionary(posting, token, doc_num, docDictionary, terms_in_doc)
                                    if token_split[0] in term_dictionary:
                                        term_dictionary[token_split[0]][0] += 1
                                    else:
                                        term_dictionary[token_split[0]] = []
                                        term_dictionary[token_split[0]].append(1)
                                        term_dictionary[token_split[0]].append("")
                                    __insert_to_dictionary(posting, token_split[0], doc_num, docDictionary, terms_in_doc)
                                    if token_split[1] in term_dictionary:
                                        term_dictionary[token_split[1]][0] += 1
                                    else:
                                        term_dictionary[token_split[1]] = []
                                        term_dictionary[token_split[1]].append(1)
                                        term_dictionary[token_split[1]].append("")
                                    __insert_to_dictionary(posting, token_split[1], doc_num, docDictionary, terms_in_doc)

                            # case 1.3.2: num-num-num...
                            else:
                                if token in term_dictionary:
                                    term_dictionary[token][0] += 1
                                    for x in range(0, len(token_split)):
                                        term_dictionary[token_split[x]][0] += 1
                                else:
                                    term_dictionary[token] = []
                                    term_dictionary[token].append(1)
                                    term_dictionary[token].append("")
                                    __insert_to_dictionary(posting, token, doc_num, docDictionary, terms_in_doc)
                                    for x in range(0, len(token_split)):
                                        if token_split[x] in term_dictionary:
                                            term_dictionary[token_split[x]][0] += 1
                                        else:
                                            term_dictionary[token_split[x]] = []
                                            term_dictionary[token_split[x]].append(1)
                                            term_dictionary[token_split[x]].append("")
                                        __insert_to_dictionary(posting, token_split[x], doc_num, docDictionary, terms_in_doc)

                    # case 1.4: $num-word
                    elif token[0] == '$':
                        if len(token_split[0]) > 1:
                            token_split[1] = token_split[1].lower()
                            if is_number(token[1]) and (token_split[1] == "million" or token_split[1] == "billion" \
                                    or token_split[1] == "trillion"):
                                token = token.replace(",", "")
                                token_split = token.split("-")
                                index = insert_number(text, token_split[0], token_split[1],  token_split[1].lower(),
                                                      term_dictionary, posting, doc_num, docDictionary, index, terms_in_doc)
                                index = index - 1

            # case 2: the token is a month, for example: May, June
            elif __is_valid_date(text, token_lower, next_token_lower, index, index_last_token):
                if token_lower in __months_set:
                    if index != index_last_token and next_token.isnumeric(): # the next token is a number, for example: 1988
                        if 0 < int(next_token) <= 31:
                            __insert_dates(posting, term_dictionary, next_token, token_lower, '',doc_num, docDictionary, terms_in_doc)
                            index += 1
                        elif 0 < int(next_token) <= 2800:
                            __insert_dates(posting, term_dictionary, '', token_lower, next_token,doc_num, docDictionary, terms_in_doc)
                            index += 1
                        else:
                            if token_lower in __stop_words:
                                pass
                            else:
                                if token in term_dictionary:
                                    term_dictionary[token][0] += 1
                                else:
                                    term_dictionary[token] = []
                                    term_dictionary[token].append(1)
                                    term_dictionary[token].append("")
                                __insert_to_dictionary(posting, token, doc_num, docDictionary, terms_in_doc)
                    else:
                        if token_lower in __stop_words:
                            pass
                        else:
                            if token in term_dictionary:
                                term_dictionary[token][0] += 1
                            else:
                                term_dictionary[token] = []
                                term_dictionary[token].append(1)
                                term_dictionary[token].append("")
                            __insert_to_dictionary(posting, token, doc_num, docDictionary, terms_in_doc)

                # case 3: the token is a number and the next token is a month, for example: 12 May 1991
                elif index + 2 < index_last_token + 1 and token_lower.isnumeric() and 0 < int(token_lower) <= 31 \
                        and next_token.lower() in __months_set and (__clean_token(text[index + 2])).isnumeric() \
                        and 0 < int(__clean_token(text[index + 2])) < 2800:
                    __insert_dates(posting, term_dictionary, token_lower, next_token.lower(),
                                   (__clean_token(text[index + 2])).lower(),doc_num, docDictionary, terms_in_doc)
                    index += 2

                # case 3.1: the token is a number and the next token is a month, for example: 13 May, 4 June
                elif token_lower.isnumeric() and 0 < int(token_lower) <= 31 and next_token.lower() in __months_set:
                    __insert_dates(posting, term_dictionary, token_lower, next_token.lower(), "", doc_num, docDictionary, terms_in_doc)
                    index += 1

                # case 3.2: the token is a number and the next token is a month, for example: 1988 May, 88 June
                elif token_lower.isnumeric() and 0 < int(token_lower) <= 2800 and next_token.lower() in __months_set:
                    __insert_dates(posting, term_dictionary, "", next_token.lower(), token_lower, doc_num, docDictionary, terms_in_doc)
                    index += 1

                elif '.' in token and len(token.split(".")) == 3:
                    date_token = token.split(".")
                    day = date_token[0]
                    months = date_token[1]
                    year = date_token[2]
                    __insert_dates(posting, term_dictionary, day, months, year, doc_num, docDictionary, terms_in_doc)
                    index += 1

            # case 5: regular word
            elif __is_valid_word(token, token_lower):
                if token_lower in __stop_words:
                    index += 1
                    continue
                if token_lower in corpus_city_dictionary:
                    if doc_num in corpus_city_dictionary[token_lower][1]:
                        corpus_city_dictionary[token_lower][1][doc_num].append(index)
                    else:
                        corpus_city_dictionary[token_lower][1][doc_num] = [index]
                if token[0].isupper():
                    if token.isupper():
                        if (stemmer):
                            if token_lower not in stemmer_dictionary:
                                tmp = token_lower
                                token_lower = ps.stem(token_lower)
                                token_upper = token_lower.upper()
                                stemmer_dictionary[tmp] = token_lower
                            else:
                                token_lower = stemmer_dictionary[token_lower]
                                token_upper = token_lower.upper()
                        if token_upper in term_dictionary:
                            term_dictionary[token_upper][0] += 1
                            __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                        elif token_lower in term_dictionary:
                            term_dictionary[token_lower][0] += 1
                            __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                        else:
                            term_dictionary[token_upper.lower()] = []
                            term_dictionary[token_upper.lower()].append(1)
                            term_dictionary[token_upper.lower()].append("")
                            __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                    else:
                        if (stemmer):
                            if token_lower not in stemmer_dictionary:
                                tmp = token_lower
                                token_lower = ps.stem(token_lower)
                                token_upper = token_lower.upper()
                                stemmer_dictionary[tmp] = token_lower
                            else:
                                token_lower = stemmer_dictionary[token_lower]
                                token_upper = token_lower.upper()
                        if token_upper in term_dictionary:
                            term_dictionary[token_upper][0] += 1
                            __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                        elif token_lower in term_dictionary:
                            term_dictionary[token_lower][0] += 1
                            __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                        else:
                            term_dictionary[token_upper] = []
                            term_dictionary[token_upper].append(1)
                            term_dictionary[token_upper].append("")
                            __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                else:
                    if (stemmer):
                        if token_lower not in stemmer_dictionary:
                            tmp = token_lower
                            token_lower = ps.stem(token_lower)
                            token_upper = token_lower.upper()
                            stemmer_dictionary[tmp] = token_lower
                        else:
                            token_lower = stemmer_dictionary[token_lower]
                            token_upper = token_lower.upper()
                    if token_lower in term_dictionary:
                        term_dictionary[token_lower][0] += 1
                        __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                    elif token_upper in term_dictionary:
                        term_dictionary[token_lower] = term_dictionary[token_upper]
                        term_dictionary[token_lower][0] += 1
                        del term_dictionary[token_upper]
                        __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                    else:
                        term_dictionary[token_lower] = []
                        term_dictionary[token_lower].append(1)
                        term_dictionary[token_lower].append("")
                        __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)

            # case 4: if the first char is a digit or "$"
            elif __is_valid_number(token):
                index = insert_number(text, token, next_token, next_token_lower, term_dictionary,
                              posting, doc_num, docDictionary, index, terms_in_doc)
            # case 5: if contin /
            elif '/' in token:
                token_split = token.split('/')
                only_words = True
                for word in token_split:
                    if not word.isalpha():
                        only_words = False
                if only_words:
                    for x in range(0, len(token_split)):  # insert every word
                        token = token_split[x]
                        token_lower = token.lower()
                        if token_lower in __stop_words:
                            index += 1
                            continue
                        token_upper = token.upper()
                        if token_lower in corpus_city_dictionary:
                            if doc_num in corpus_city_dictionary[token_lower][1]:
                                corpus_city_dictionary[token_lower][1][doc_num].append(index)
                            else:
                                corpus_city_dictionary[token_lower][1][doc_num] = [index]
                        if token[0].isupper():
                            if token.isupper():
                                if (stemmer):
                                    if token_lower not in stemmer_dictionary:
                                        tmp = token_lower
                                        token_lower = ps.stem(token_lower)
                                        token_upper = token_lower.upper()
                                        stemmer_dictionary[tmp] = token_lower
                                    else:
                                        token_lower = stemmer_dictionary[token_lower]
                                        token_upper = token_lower.upper()
                                if token_upper in term_dictionary:
                                    term_dictionary[token_upper][0] += 1
                                    __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                                elif token_lower in term_dictionary:
                                    term_dictionary[token_lower][0] += 1
                                    __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                                else:
                                    term_dictionary[token_upper.lower()] = []
                                    term_dictionary[token_upper.lower()].append(1)
                                    term_dictionary[token_upper.lower()].append("")
                                    __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                        else:
                            if (stemmer):
                                if token_lower not in stemmer_dictionary:
                                    tmp = token_lower
                                    token_lower = ps.stem(token_lower)
                                    token_upper = token_lower.upper()
                                    stemmer_dictionary[tmp] = token_lower
                                else:
                                    token_lower = stemmer_dictionary[token_lower]
                                    token_upper = token_lower.upper()
                            if token_upper in term_dictionary:
                                term_dictionary[token_upper][0] += 1
                                __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
                            elif token_lower in term_dictionary:
                                term_dictionary[token_lower][0] += 1
                                __insert_to_dictionary(posting, token_lower, doc_num, docDictionary, terms_in_doc)
                            else:
                                term_dictionary[token_upper] = []
                                term_dictionary[token_upper].append(1)
                                term_dictionary[token_upper].append("")
                                __insert_to_dictionary(posting, token_upper.lower(), doc_num, docDictionary, terms_in_doc)
        index += 1
    if doc_num in docDictionary:
        docDictionary[doc_num].number_of_terms = len(terms_in_doc)
        num1 = 0
        for key in terms_in_doc:
            num1 += terms_in_doc[key]
        docDictionary[doc_num].length = num1
        docDictionary[doc_num].terms_in_doc = terms_in_doc

# That func analyze that token and preparation the number for saving
def insert_number(text,  token, next_token, next_token_lower, term_dictionary, posting, doc_num, docDictionary, index
                  , terms_in_doc):
    fraction = False
    fraction_val = ""
    final = ""  # the final number
    if index < len(text) - 1:
        if "/" in next_token:
            fraction = True
            index += 1
            fraction_val = next_token
            next_token = ""
            if index < len(text) - 1:
                next_token = __clean_token(text[index + 1])
                next_token_lower = next_token.lower()
    num_to_final = token.replace("$", "")
    num = num_to_final.replace(",", "")
    num = num.replace("m", "")
    num = num.replace("bn", "")
    tmp_num = num.replace(".", "")
    number = 0.0
    if "/" in num:
        fraction_val = num
        number = 0
    elif tmp_num.isnumeric():
        number = float(num)
    elif "B" in num:
        num = num.replace("B", "")
        if num.isnumeric():
            number = float(num)
            next_token_lower = "billion"
    # case 4.1: % number for example: Number%, Number percent, Number percentage
    if "%" in token or next_token_lower == "percent" or next_token_lower == "percentage":
        if "%" not in num_to_final:
            num_to_final = num_to_final + "%"
        final = num_to_final
        if next_token_lower == "percent" or next_token_lower == "percentage":
            index += 1
        if final in term_dictionary:
            term_dictionary[final][0] += 1
        else:
            term_dictionary[final] = []
            term_dictionary[final].append(1)
            term_dictionary[final].append("")
        __insert_to_dictionary(posting, final, doc_num, docDictionary, terms_in_doc)

    # case 4.2: for example: $price, price m Dollars, $price billion, price fraction Dollars
    elif token[0] == "$" or next_token_lower == "dollars" \
            or next_token_lower == "m" or next_token_lower == "bn":
        if token[0] == "$":
            if next_token_lower == "million" or next_token_lower == "billion" or next_token_lower == "trillion":
                index += 1
                if next_token_lower == "billion":
                    number *= 1000
                elif next_token_lower == "trillion":
                    number *= 1000000
                if number - int(number) == 0:
                    number = int(number)
                num_to_final = str(number)
                if fraction:  # there is a fraction
                    final = num_to_final + " " + fraction_val + " M Dollars"
                else:
                    final = num_to_final + " M Dollars"
                if final in term_dictionary:
                    term_dictionary[final][0] += 1
                else:
                    term_dictionary[final] = []
                    term_dictionary[final].append(1)
                    term_dictionary[final].append("")
                __insert_to_dictionary(posting, final, doc_num, docDictionary, terms_in_doc)
            else:
                if number > 1000000:
                    number = number / 1000000
                    if number.is_integer():
                        number = int(number)
                    num_to_final = str(number)
                    if fraction:  # there is a fraction
                        final = num_to_final + " " + fraction_val + " M Dollars"
                    else:
                        final = num_to_final + " M Dollars"
                    if final in term_dictionary:
                        term_dictionary[final][0] += 1
                    else:
                        term_dictionary[final] = []
                        term_dictionary[final].append(1)
                        term_dictionary[final].append("")
                    __insert_to_dictionary(posting, final, doc_num, docDictionary, terms_in_doc)
                else:
                    if fraction:  # there is a fraction
                        final = num_to_final + " " + fraction_val + " Dollars"
                    else:
                        final = num_to_final + " Dollars"
                    if final in term_dictionary:
                        term_dictionary[final][0] += 1
                    else:
                        term_dictionary[final] = []
                        term_dictionary[final].append(1)
                        term_dictionary[final].append("")
                    __insert_to_dictionary(posting, final, doc_num, docDictionary, terms_in_doc)
        elif next_token_lower == "m" or next_token_lower == "bn":
            if index < len(text) - 2 and (__clean_token(text[index + 2])).lower() == "dollars":
                index += 2
                if next_token_lower == "bn":
                    number *= 1000
                if number - int(number) == 0:
                    number = int(number)
                num_to_final = str(number)
                if fraction:  # there is a fraction
                    final = num_to_final + " " + fraction_val + " M Dollars"
                else:
                    final = num_to_final + " M Dollars"
                if final in term_dictionary:
                    term_dictionary[final][0] += 1
                else:
                    term_dictionary[final] = []
                    term_dictionary[final].append(1)
                    term_dictionary[final].append("")
                __insert_to_dictionary(posting, final, doc_num, docDictionary, terms_in_doc)
        else:
            if next_token_lower == "dollars":
                index += 1
            if number < 1000000:
                if fraction:  # there is a fraction
                    final = num_to_final + " " + fraction_val + " Dollars"
                else:
                    final = num_to_final + " Dollars"
                if final in term_dictionary:
                    term_dictionary[final][0] += 1
                else:
                    term_dictionary[final] = []
                    term_dictionary[final].append(1)
                    term_dictionary[final].append("")
                __insert_to_dictionary(posting, final, doc_num, docDictionary, terms_in_doc)
            else:
                number = number / 1000000
                if number.is_integer():
                    number = int(number)
                num_to_final = str(number)
                if fraction:  # there is a fraction
                    final = num_to_final + " " + fraction_val + " M Dollars"
                else:
                    final = num_to_final + " M Dollars"
                if final in term_dictionary:
                    term_dictionary[final][0] += 1
                else:
                    term_dictionary[final] = []
                    term_dictionary[final].append(1)
                    term_dictionary[final].append("")
                __insert_to_dictionary(posting, final, doc_num, docDictionary, terms_in_doc)
    # case 4.3: for example: price billion U.S. dollars, price trillion U.S. dollars
    elif index < len(text) - 3 and (
            next_token_lower == "million" or next_token_lower == "billion" or next_token_lower == "trillion") \
            and (__clean_token(text[index + 2]) == "U.S" and (__clean_token(text[index + 3])).lower() == "dollars"):
        index += 3
        if next_token_lower == "billion":
            number *= 1000
        elif next_token_lower == "trillion":
            number *= 1000000
        if number.is_integer():
            number = int(number)
        num_to_final = str(number)
        if fraction:  # there is a fraction
            final = num_to_final + " " + fraction_val + " M Dollars"
        else:
            final = num_to_final + " M Dollars"
        if final in term_dictionary:
            term_dictionary[final][0] += 1
        else:
            term_dictionary[final] = []
            term_dictionary[final].append(1)
            term_dictionary[final].append("")
        __insert_to_dictionary(posting, final, doc_num, docDictionary, terms_in_doc)
    # case 4.4: regular number for example: 123 Thousand, 1010.56, 22 3/4, 7 Trillion
    else:
        num = token.replace(",", "")
        if "/" in num:
            fraction_val = num
            number = 0.0
        if num.isnumeric():
            number = float(num)
        final = 0

        if 'number' in locals():
            if number > 100000000000 or next_token_lower == "trillion":
                if number > 100000000000:
                    number = number / 100000000000
                if number.is_integer():
                    number = int(number) * 1000
                if fraction:
                    final = str(number) + " " + fraction_val + "B"
                else:
                    final = str(number) + "B"
            elif number > 1000000000 or next_token_lower == "billion":
                if number > 1000000000:
                    number = number / 1000000000
                if number.is_integer():
                    number = int(number)
                if fraction:
                    final = str(number) + " " + fraction_val + "B"
                else:
                    final = str(number) + "B"
            elif number > 1000000 or next_token_lower == "million":
                if number > 1000000:
                    number = number / 1000000
                if number.is_integer():
                    number = int(number)
                if fraction:
                    final = str(number) + " " + fraction_val + "M"
                else:
                    final = str(number) + "M"
            elif number > 1000 or next_token_lower == "thousand":
                if number > 1000:
                    number = number / 1000
                if number.is_integer():
                    number = int(number)
                if fraction:
                    final = str(number) + " " + fraction_val + "K"
                else:
                    final = str(number) + "K"
            else:
                number = int(number)
                final = str(number)
                if fraction:
                    final = str(number) + " " + fraction_val
            if next_token_lower == "thousand" or next_token_lower == "million":
                index += 1
            if next_token_lower == "trillion" or next_token_lower == "billion":
                index += 1
            if final in term_dictionary:
                term_dictionary[final][0] += 1
            else:
                term_dictionary[final] = []
                term_dictionary[final].append(1)
                term_dictionary[final].append("")
            __insert_to_dictionary(posting, final, doc_num, docDictionary, terms_in_doc)
    return index

# That func send the docs 1 by 1 to the parse_text func
def parse_docs(posting, term_dictionary, corpus_city_dictionary, text_dictionary, docDictionary, idx, stemmer, posting_path):
    while len(text_dictionary) > 0:
        item = text_dictionary.popitem()
        parse_text(posting, term_dictionary, corpus_city_dictionary, item[1], item[0], docDictionary, stemmer)
    del text_dictionary
    saveFiles(idx, posting, docDictionary, posting_path)
    del posting
    del docDictionary


def parse_queries(source_path, destination_path, query, stemmer, semantic):
    index = 0
    list_save_queries = []

    if source_path == "":
        list_save_queries.append("query_post"+str(index))
        sem = ""
        if semantic:
            sem += " " + add_sim_word(query)
        parse_query(query, sem, index, stemmer, destination_path)
    else:
        queries_file = open(source_path, 'r+')
        queries = queries_file.read()
        queries_list_num = re.compile('Number:(.*?)<title>', re.DOTALL).findall(queries)
        queries_list = re.compile('<title>(.*?)<desc>', re.DOTALL).findall(queries)
        queries_desc_list = re.compile('<desc>(.*?)<narr>', re.DOTALL).findall(queries)
        queries_file.close()
        for query in queries_list:
            query = query.replace('\n', "")
            query = query[1:-1]
            desc = queries_desc_list[index].replace('\n'," ")
            desc = desc.replace('Description:','')
            query_num = queries_list_num[index].replace('\n', "")
            query_num = query_num.replace(" ", "")
            list_save_queries.append("query_post"+str(query_num))
            sem = desc
            if semantic:
                sem += " " + add_sim_word(query)
            parse_query(query, sem, query_num, stemmer, destination_path)
            index += 1
    return list_save_queries


def add_sim_word(query):
    url = "https://api.datamuse.com/words?ml=";
    query = query.split()
    sim_word = ""
    for word in query:
        json_url = urlopen(url + word+"&max=2")
        data = json.loads(json_url.read())
        for key in data:
            if key['score'] < 10000:
                break
            sim_word += (str(key['word']) + " ")
    return sim_word


def parse_query(query_title, query_sem, idx, stemmer, path):
    final_query_term = {}

    term_in_query_title = {}
    parse_text(term_in_query_title, {}, {}, query_title, idx, {}, stemmer)
    for term in term_in_query_title:
        final_query_term[term.lower()] = term_in_query_title[term]
        final_query_term[term.lower()].term_rank = 1

    term_in_query_sem = {}
    parse_text(term_in_query_sem, {}, {}, query_sem, idx, {}, stemmer)
    for term in term_in_query_sem:
        if term.lower() in final_query_term:
            final_query_term[term.lower()].term_rank = 1
        else:
            final_query_term[term.lower()] = term_in_query_sem[term]
            final_query_term[term.lower()].term_rank = 0.5

    save_query(idx, final_query_term, path)
    del term_in_query_title
    del term_in_query_sem
    del final_query_term


# That func save the tmp post files.
def saveFiles(idx, posting, docDictionary, posting_path):
    sort_key = sorted(posting)
    sort_posting={}
    for key in sort_key:
        sort_posting[key] = posting[key]
    file = open(posting_path + "/post" + str(idx) + ".pkl", "wb+")
    pickle.dump(sort_posting, file, pickle.HIGHEST_PROTOCOL)
    file.close()
    file = open(posting_path + "/doc" + str(idx) + ".pkl", "wb+")
    pickle.dump(docDictionary, file, pickle.HIGHEST_PROTOCOL)
    file.close()


def save_query(idx, term_in_query, path):
    sort_key = sorted(term_in_query)
    sort_posting = {}
    for key in sort_key:
        sort_posting[key] = term_in_query[key]
    file = open(path + "/query_post" + str(idx) + ".pkl", "wb+")
    pickle.dump(sort_posting, file, pickle.HIGHEST_PROTOCOL)
    file.close()
