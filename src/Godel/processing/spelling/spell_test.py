from nltk.stem.porter import PorterStemmer
from nltk.corpus import brown

import sys
from collections import defaultdict
import operator

from bloom import BloomFilter

def sortby(nlist ,n, reverse=0):
    nlist.sort(key=operator.itemgetter(n), reverse=reverse)
 
class mydict(dict):
    def __missing__(self, key):
        return 0


class spelling:
    def __init__(self):
        self.stemmer = PorterStemmer()
        
    def __specialhash(self, s):
        s = s.lower()
        s = s.replace("z", "s")
        s = s.replace("h", "")
        for i in [chr(ord("a") + i) for i in range(26)]:
            s = s.replace(i+i, i)
        print s
        s = self.stemmer.stem(s)
        return s

    def test(self, token):
        hashed = self.__specialhash(token)
        print hashed
        if self.bf.InFilter(hashed):
            print "Yes!"
            
        return "I can't find similar word in my learned db"

    def learn(self, listofsentences=[], n=126733):
        self.bf = BloomFilter(1090177, 4)
        i = 0
        for sent in brown.raw():
            if i >= n:
                break
            for word in sent:
                self.bf.Insert(word.lower())
                i += 1
                
        self.bf.PrintStats()

        
def demo():
    d = spelling()
    d.learn()
    # choice of words to be relevant related to the brown corpus
    for i in "birdd, oklaoma, emphasise, bird, carot".split(", "):
        print i, "-", d.test(i)
 
if __name__ == "__main__":
    demo()
