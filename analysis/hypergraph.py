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
            head = token
            tail = self.tokenized[idx+1]
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

    def characterize_edge(self, tag_set):
        characterizer = [
            'pos',
        ]
        
        for tag in tag_set:
            head, data, tail = tag
            edge = self.atoms.add_edge(head, dependent, edge_data=[tag], edge_type=edge_type,
                                       with_merge=False)
                
    def get_hypergraph(self):
        return self.atoms
    
    def word_position(self, search_word):
        tokens = nltk.word_tokenize(self.sentence[0])
        for idx, word in enumerate(tokens):
            if word == search_word:
                return (idx, word)
            
    def features_in(self, features):
        types = ['pos']
        
        for feature in features:
            tag  = feature[0]
            head = feature[1]
            dependent = feature[2]
            
            tag_type = self.characterize_tag(tag)
            edgeType = (tag_type != None and tag_type or 'feature')
            ## debug(edge_type)


            if tag in types:
                edge_type = tag
            else:
                edge_type = edgeType
                
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
        self.sentence_analyze()
        
    def sentence_analyze(self):
        self.atoms.to_dot_file(primary_type='sentence')
    
    


        
        


