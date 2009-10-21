import sys
sys.path.append('data/conceptnet/')
from csc.util.persist import get_picklecached_thing
from csc.conceptnet4.models import Concept
from csc.conceptnet4.analogyspace import conceptnet_2d_from_db
from csc.nl import get_nl
import csc

from utils.debug import *

import itertools
import operator

class DivsiHelper:
    def __init__(self):
        self.EuroNL = get_nl('en')

    def sortDictionary(self, Dictionary):
        return sorted(Dictionary.iteritems(), key=lambda x:(x[0], x[1]), reverse=True)

    def byFeatureTag(self, universal_sentence):
        for x in universal_sentence.features:
            tag, left, right = x
            yield {'tag':tag, 'l':left, 'r':right}
            
    def interestingTags(self, univ_sentence):
        ## exhaustive combinations of the interesting tags
        totalTags = []
        iTags = ['_subj', '_obj', '_predadj']
        for eachTag in self.byFeatureTag(univ_sentence):
            if eachTag['tag'] in iTags:
                concept = self.Conceptable(eachTag)
                if concept:
                    totalTags.append(concept['l'])
                    totalTags.append(concept['r'])
                    
        for combinations in itertools.combinations(totalTags, 2):
            if combinations[0] != combinations[1]:
                yield combinations
        
    def Conceptable(self, tag):
        if self.EuroNL.is_stopword(tag['l']):
            return False
        if self.EuroNL.is_stopword(tag['r']):
            return False
        if self.EuroNL.is_blacklisted(tag['l']):
            return False
        if self.EuroNL.is_blacklisted(tag['r']):
            return False

        L   = self.EuroNL.normalize(tag['l'])
        R   = self.EuroNL.normalize(tag['r'])
        Tag = self.EuroNL.normalize(tag['tag'])
        return {'l':L, 'r':R, 'tag':Tag}
    
class Divsi:
    svd = None
    def __init__(self):
        self.helper = DivsiHelper()
        self.cnet_normalized = conceptnet_2d_from_db('en').normalized()
        self.analogySpace = self.cnet_normalized.svd()
        self.EN_NL = get_nl('en')

    def load_svd(self, k=100):
        svd = self.tensor.svd(k=k)
        return svd
    
    def concept_similarity(self, universal_word):
        similarity = {}
        common = {}
        for interesting in self.helper.interestingTags(universal_word):
            L = interesting[0]
            R = interesting[1]
            try:
                left  = self.analogySpace.weighted_u_vec(L)
                right = self.analogySpace.weighted_u_vec(R)
                similar = left.hat() * right.hat()
                common[L] = self.analogySpace.u_dotproducts_with(L).top_items(10)
                common[R] = self.analogySpace.u_dotproducts_with(R).top_items(10)

                similarity[similar] = [interesting[0], interesting[1]]
            except:
                pass

        return self.helper.sortDictionary(simularity)

            


    
    
