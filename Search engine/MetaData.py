# class MetaData
# the meta data of term.
class MetaData:
    def __init__(self, df ,frequencyInDoc):
        self.df = df
        self.frequencyInDoc = frequencyInDoc
        self.term_rank = 0;