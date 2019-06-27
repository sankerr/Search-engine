# class Document present the document in the corpus and
# is attributes.

class Document:
    def __init__(self, path, docNum, city, date, number_of_terms, title, language):
        self.path = path
        self.docNum = docNum
        self.city = city
        self.date = date
        self.maxTf = 1
        self.length = 0
        self.number_of_terms = number_of_terms
        self.title = title
        self.language = language
        self.terms_in_doc = {}