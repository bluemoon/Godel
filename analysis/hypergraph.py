#import networkx
from structures.atoms import Atoms
from data.prepositions import prepositions
from rules import Triple
from rules import prep_ruleset
from rules import triple_ruleset

from utils.debug import *

import nltk

class HG:
    def __init__(self, sentence):
        self.atoms = Atoms()
        self.sentence = sentence
        self.tokenized = nltk.word_tokenize(sentence[0])
        self.prep_count = 0
        self.useful = []
        
        for idx, token in enumerate(self.tokenized[:-1]):
            #self.atoms.add_node(token, node_data=idx)
            head = token #'%d_%s' % (idx, token)
            tail = self.tokenized[idx+1] #'%d_%s' % (idx+1, self.tokenized[idx+1])
            
            self.atoms.add_edge(head, tail, edge_data=[idx], head_data=[idx],
                                tail_data=[idx+1], with_merge=True, edge_type='sentence')

            if token in prepositions:
                prep_idx = prepositions.index(token)
                self.atoms.add_edge(self.tokenized[idx-1], self.tokenized[idx+1],
                                    edge_data=[prepositions[prep_idx]],
                                    with_merge=False, edge_type='preposition')
                self.prep_count += 1
                
        #self.atoms.add_node(self.tokenized[-1], node_data=len(self.tokenized)+1)

    
    def word_position(self, search_word):
        tokens = nltk.word_tokenize(self.sentence[0])
        for idx, word in enumerate(tokens):
            if word == search_word:
                return (idx, word)
            
            
    def features_in(self, features):
        #debug(self.sentence[1])
        for feature in features:
            tag  = feature[0]
            head = feature[1]
            dependent = feature[2]
            
            edge = self.atoms.add_edge(head, dependent, edge_data=[tag], edge_type='feature',
                                       with_merge=False)
        
    def frames_in(self, frames):
        for frame in frames:
            tag = '_'.join(frame[1:2])
            head = frame[3]
            dependent = frame[4]
            
            edge = self.atoms.add_edge(head, dependent, edge_data=[tag], edge_type='frame',
                                       with_merge=False)
            
    def analysis(self):
        self.triple = Triple()
        
        #self.atoms.to_dot_file(primary_type='sentence')
        self.sentence_analyze()
        
    def sentence_analyze(self):
        prep_rules = prep_ruleset(self.tokenized, self.atoms)
        prep = prep_rules.run_rules()
        debug(self.tokenized)
        debug(prep)

        if len(prep) < 1:
            self.atoms.delete_edge_by_type('preposition')

        
        #self.atoms.to_dot_file(primary_type='sentence')
        
        triple = triple_ruleset(self.tokenized, self.atoms)
        tri = triple.run_all()
        debug(tri)

        
        


