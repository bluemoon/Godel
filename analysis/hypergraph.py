#import networkx
from structures.atoms import Atoms
from data.prepositions import prepositions
from rule_engine import rule_engine

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

                
        #self.atoms.add_node(self.tokenized[-1], node_data=len(self.tokenized)+1)

    def characterize_tag(self, find_tag):
        characterizer = {
            'preposition' : prepositions,
        }
        
        for character, tags in characterizer.items():
            ## combined = list(itertools.product([character], tag))
            for tag in tags:
                if find_tag == tag:
                    return character

    def get_hypergraph(self):
        return self.atoms
    
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
            
            tag_type = self.characterize_tag(tag)
            edge_type = (tag_type != None and tag_type or 'feature')
            
            edge = self.atoms.add_edge(head, dependent, edge_data=[tag], edge_type=edge_type,
                                       with_merge=False)
        
    def frames_in(self, frames):
        for frame in frames:
            tag = '_'.join(frame[1:2])
            head = frame[3]
            dependent = frame[4]
            
            edge = self.atoms.add_edge(head, dependent, edge_data=[tag], edge_type='frame',
                                       with_merge=False)
            
    def analysis(self):
        #self.atoms.to_dot_file(primary_type='sentence')
        self.sentence_analyze()
        
    def sentence_analyze(self):
        
        #debug(self.tokenized)
        
        #if len(prep) < 1:
        #    self.atoms.delete_edge_by_type('preposition')

        #for x in prep:
        #    var_1 = x[1]['$var1']
        #    var_2 = x[1]['$var2']
        #    
        #    debug((var_1, var_2))
        #    self.atoms.add_edge(var_1, var_2, edge_data=[],
        #                        edge_type='preposition', with_merge=False)

                    
                
                
        self.atoms.to_dot_file(primary_type='sentence')

        
        #triple = triple_ruleset(self.tokenized, self.atoms)
        #tri = triple.run_all()
        #debug(tri)

        
        


