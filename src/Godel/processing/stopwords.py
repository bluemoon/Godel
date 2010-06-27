def is_other_stopword(word):
    f_handle = open('data/stopwords.txt')
    f_file = f_handle.read()
    lines = f_file.split('\n')
    if word in lines:
        return True
    else:
        return False
