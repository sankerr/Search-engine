# Class ReadFile
# That class read the corpus and splits it to a lists
# That class also take and organizes data of the doc like title, city, date and language

import json
import os
import sys
from urllib.request import urlopen

from Document import Document

__months_dictionary = {'january': '01', 'jan': '01', 'february': '02', 'feb': '02', 'march': '03', 'mar': '03',
                       'april': '04', 'apr': '04', 'may': '05', 'june': '06', 'jun': '06', 'july': '07',
                       'jul': '07',
                       'august': '08', 'aug': '08', 'september': '09', 'sep': '09', 'october': '10', 'oct': '10',
                       'november': '11', 'nov': '11', 'december': '12', 'dec': '12'}
__punctuations_set = {'[', '(', '{', '`', ')', '<', '|', '&', '~', '+', '^', '@', '*', '?', '.',
                      '>', ';', '_', '\'', ':', ']', '/', '\\', "}", '!', '=', '#', ',', '\"', '-'}

path = ""  # The path to the file
docNumList = []  # A list of all doc nums in the file
docCityList = []  # A list of all doc city in the file
docLanguageList = []  # A list of all doc language in the file
docTitleList = []  # A list of all doc title in the file
docDateList = []  # A list of all doc date of publication
textList = []  # A list of all the texts in a file
textDic = {}  # A dictionary that key is doc number and value is the text
docDictionary = {}  # A dictionary for all document in corpus
length = 0  # The number of documents in the current file (length of docNumList)
fileName = ""  # The file name of the documents. Used for part 2 of the assignment
index = 0
corpus_city_dictionary = {}
world_city_dictionary = {}

def split_doc(path_corpus="", sub_dir=""):
    global path
    global textList
    global textDic
    global length
    global fileName
    global index

    path = path_corpus
    dir = sub_dir
    for root, dirs, files in os.walk(path + "/" +dir):  # traverses the given file path.
        fileName = path + "/" + dir + "/" + files[0]
        text_file = open(os.path.join(path + "/" +dir, files[0]), 'r', encoding="ISO-8859-1")  # The encoding of text files.
        textList = text_file.read().split("</TEXT>")  # Split at </TEXT> tag.
        text_file.close()
        del textList[-1]  # The last object in the list is the garbage past the final </TEXT> tag.
        length = len(textList)
        index = len(textDic)
        idx_create = len(textDic)
        __takeDocNum()
        __takeTitleCity()
        __takeLanguageCity()
        __takeDocCity()
        __takeDocDate()
        __takeText()
        __createDocDictionary(idx_create)

# Extract the docNum from a whole Document
def __takeDocNum():
    global length
    global textList
    global docNumList

    for i in range(length):
        docNum = (textList[i].split("</DOCNO>", 1)[0]).split("<DOCNO>")[1].strip()
        docNumList.append(docNum)


# Extract the doc title from a whole Document
def __takeTitleCity():
    global length
    global textList
    global docTitleList

    for i in range(length):
        if "<TI>" in textList[i]:
            docTI = textList[i].split("</TI>")[0]
            docTI = docTI.split("<TI>")[1].split()
            TI = ""
            for word in docTI:
                TI += word
                TI += " "
            TI = TI[:-1]
            docTitleList.append(TI)
        elif "<HEADLINE>" in textList[i]:
            docTI = textList[i].split("</HEADLINE>")[0]
            docTI = docTI.split("<HEADLINE>")[1].split()
            TI = ""
            for word in docTI:
                if not word[0] == "<":
                    TI += word
                    TI += " "
            TI = TI[:-1]
            docTitleList.append(TI)
        else:
            docTitleList.append("")


# Extract the doc language from a whole Document
def __takeLanguageCity():
    global length
    global textList
    global docLanguageList
    global __punctuations_set

    for i in range(length):
        if "<F P=105>" in textList[i]:
            tmpList = textList[i].split("<F P=105>")[1].split()
            tmp = __clean_token(tmpList[0])
            if tmp == "":
                docLanguageList.append("")
            else:
                language = tmp[0].upper() + tmp[1:].lower()
                if language == "The":
                    docLanguageList.append("")
                else:
                    docLanguageList.append(language)
        else:
            docLanguageList.append("")

# Extract the doc city from a whole Document
def __takeDocCity():
    global length
    global textList
    global docCityList
    global corpus_city_dictionary

    for i in range(length):
        if "<F P=104>" in textList[i]:
            tmpCityList = textList[i].split("<F P=104>")[1].split()
            docCity_lower = tmpCityList[0].lower()
            idx = 1
            size = len(tmpCityList)
            while not docCity_lower in corpus_city_dictionary and idx < 4 and idx < size:
                docCity_lower += " "
                docCity_lower += tmpCityList[idx].lower()
                idx += 1
            if docCity_lower in corpus_city_dictionary:
                city = docCity_lower[0].upper() + docCity_lower[1:len(docCity_lower)]
                docCityList.append(city)
            else:
                docCityList.append("")
        else:
            docCityList.append("")


# Extract the docDate from a whole Document
def __takeDocDate():
    global length
    global textList
    global docDateList

    for i in range(length):
        if "<DATE1>" in textList[i]:
            docDate = textList[i].split("</DATE1>")[0]
            docDate = textList[i].split("<DATE1>")[1].split()
            if docDate[0].lower() in __months_dictionary:
                months = __months_dictionary[docDate[0].lower()]
                day = docDate[1]
                year = docDate[2]
                if year[len(year) - 1] == '*':
                    year = year[:-1]
                if not year.isnumeric():
                    year = ""
                if year.isnumeric() and 0 < int(year) < 100:
                    year = "19" + year
                if len(day) == 1:
                    day = "0" + day
                if year == "":
                    docDateList.append(months + "-" + day)
                else:
                    docDateList.append(year + "-" + months + "-" + day)
            elif docDate[1].lower() in __months_dictionary:
                months = __months_dictionary[docDate[1].lower()]
                day = docDate[0]
                year = docDate[2]
                if year[len(year)-1] == '*':
                    year = year[:-1]
                if not year.isnumeric():
                    year=""
                if year.isnumeric() and 0 < int(year) < 100:
                    year = "19" + year
                if len(day) == 1:
                    day = "0" + day
                if year == "":
                    docDateList.append(months+"-"+day)
                else:
                    docDateList.append(year + "-" + months + "-" + day)
            elif docDate[0] == "000" and docDate[1] == "000":
                year = docDate[2]
                if year[len(year)-1] == '*':
                    year = year[:-1]
                if not year.isnumeric():
                    year=""
                if year.isnumeric() and 0 < int(year) < 100:
                    year = "19" + year
                docDateList.append(year)

        elif "<DATE>" in textList[i]:
            docDate = textList[i].split("</DATE>")[0]
            docDate = textList[i].split("<DATE>")[1].split()
            if docDate[0].isnumeric() and len(docDate[0]) == 6:
                day = docDate[0][4:]
                months = docDate[0][2:4]
                year = docDate[0][:-4]
                year = "19" + year
                docDateList.append(year + "-" + months + "-" + day)
            if not len(docDate[0]) == 6:
                idx = 1
                while not docDate[idx].lower() in __months_dictionary:
                    idx += 1
                months = __months_dictionary[docDate[idx].lower()]
                day = docDate[idx+1]
                if ',' in day:
                    day = docDate[idx+1][:-1]
                year = docDate[idx+2]
                if ',' in year:
                    year = docDate[idx+2][:-1]
                if 0 < int(year) < 100:
                    year = "19" + year
                if len(day) == 1:
                    day = "0" + day
                docDateList.append(year + "-" + months + "-" + day)

        else:
            docDateList.append("")


# Extract the clean text
def __takeText():
    global length
    global textList
    global textDic
    global index

    for i in range(length):
        text = textList[i].split("<TEXT>")[1].strip()
        # remove problematic or meaningless strings that clutter the corpus
        text = text.replace('\n', " ")
        text = text.replace('CELLRULE', " ")
        text = text.replace('TABLECELL', " ")
        text = text.replace('CVJ="C"', " ")
        text = text.replace('CHJ="C"', " ")
        text = text.replace('CHJ="R"', " ")
        text = text.replace('CHJ="L"', " ")
        text = text.replace('TABLEROW', " ")
        text = text.replace('ROWRULE', " ")
        text = text.replace('>', " ")
        text = text.replace('<', " ")
        text = ' '.join(text.split())
        textDic[docNumList[index]] = text
        index += 1


# creates the dictionary to be returned
def __createDocDictionary(idx):
    global length
    global docNumList
    global docCityList
    global docDictionary
    global fileName
    global docLanguageList
    global docTitleList

    length = len(docNumList)
    while idx < length:
        docDictionary[docNumList[idx]] = Document(fileName, docNumList[idx],
                docCityList[idx], docDateList[idx], "", docTitleList[idx], docLanguageList[idx])
        idx += 1

# Delete Reader's data structures
def __reset():
    global docNumList
    global docCityList
    global docDateList
    global docLanguageList
    global docTitleList
    global textList
    global fileName
    global length
    global textDic
    global docDictionary
    global index
    global world_city_dictionary

    docNumList = []
    docCityList = []
    docDateList = []
    docLanguageList = []
    docTitleList = []
    textList = []
    textDic = {}
    docDictionary = {}
    length = 0
    index = 0
    fileName = ""
    world_city_dictionary = {}


def read_doc(doc_num, file_path):
    global docNumList
    global textList
    global length

    text_file = open(os.path.join(file_path), 'r', encoding="ISO-8859-1")
    textList = text_file.read().split("</TEXT>")  # Split at </TEXT> tag.
    text_file.close()
    del textList[-1]  # The last object in the list is the garbage past the final </TEXT> tag.

    length = len(textList)
    __takeDocNum()
    __takeText()

    text = ""
    for i in range(length):
        if docNumList[i] == doc_num:
            text = textList[i]
            break
    return text


def creat_world_city_dictionary():
    global world_country_dictionary

    url = "https://restcountries.eu/rest/v2/all"
    json_url = urlopen(url)
    data = json.loads(json_url.read())
    country_dict = {}
    for l in data:
        pop = float(l["population"])
        final = ""
        if pop > 100000000000:
            pop = pop / 100000000000
            if pop.is_integer():
                pop = int(pop) * 1000
            final = str(pop) + "B"
        elif pop > 1000000000:
            if pop > 1000000000:
                pop = pop / 1000000000
            if pop.is_integer():
                pop = int(pop)
            final = str(pop) + "B"
        elif pop > 1000000:
            if pop > 1000000:
                pop = pop / 1000000
            if pop.is_integer():
                pop = int(pop)
            final = str(pop) + "M"
        elif pop > 1000:
            if pop > 1000:
                pop = pop / 1000
            if pop.is_integer():
                pop = int(pop)
            final = str(pop) + "K"
        country_dict[l["alpha2Code"]] = [l["name"], l["currencies"][0]["code"], final]
    file_path = resource_path("Resources/worldcities.csv")
    database = open(file_path, "rb+")
    idx = 0
    for line in database:
        if not idx == 0:
            line = str(line).split(',')
            Country = line[5][1:-1]
            City = line[1][1:-1].lower()
            if Country in country_dict and City not in world_city_dictionary:
                d = country_dict[Country]
                world_city_dictionary[City] = [d[0], d[1], d[2]]
        idx += 1


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def creat_corpus_city_dictionary(path_corpus, sub_dir):
    global corpus_city_dictionary

    path = path_corpus
    dir = sub_dir
    for root, dirs, files in os.walk(path + "/" + dir):  # traverses the given file path.
        text_file = open(os.path.join(path + "/" + dir, files[0]), 'r',
                         encoding="ISO-8859-1")  # The encoding of text files.
        textList = text_file.read().split("</TEXT>")  # Split at </TEXT> tag.
        text_file.close()
        del textList[-1]  # The last object in the list is the garbage past the final </TEXT> tag.
        length = len(textList)
        for i in range(length):
            if "<F P=104>" in textList[i]:
                tmpCityList = textList[i].split("<F P=104>")[1].split()
                docCity_lower = tmpCityList[0].lower()
                idx = 1
                size = len(tmpCityList)
                while not docCity_lower in world_city_dictionary and idx < 4 and idx < size:
                    docCity_lower += " "
                    docCity_lower += tmpCityList[idx].lower()
                    idx += 1
                if docCity_lower in world_city_dictionary:
                    if not docCity_lower in corpus_city_dictionary:
                        corpus_city_dictionary[docCity_lower] = [world_city_dictionary[docCity_lower]]


def __clean_token(token):
    token_length = len(token)
    while (token_length > 0) and (token[0] in __punctuations_set or token[0].isnumeric()):
        token = token[1:]
        token_length -= 1

    while (token_length > 1) and (token[token_length - 1] in __punctuations_set or token[0].isnumeric()):
        token = token[:-1]
        token_length -= 1

    return token
