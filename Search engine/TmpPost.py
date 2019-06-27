# Class tmp post
# That class represent the tmp posting object
# The object fields are:
# post_num - the number of the posting file that that dictionary toke from
# dictionary - the term dictionary
# keys - the terms
# num_of_update - the number of time that tmp file toke the 10,000 next values from the tmp post.

class TmpPost:
    def __init__(self, post_num, dictionary, keys, num_of_update):
        self.post_num = post_num
        self.dictionary = dictionary
        self.keys = keys
        self.num_of_update = num_of_update
