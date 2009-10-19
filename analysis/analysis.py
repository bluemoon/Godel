# -*- coding: utf-8 -*-
from utils.debug import *

from relex_analysis import relex_analyze
from structures.containers import word
from processing.tagger import tagger
from hypergraph import HG

from rule_engine import rule_engine

import nltk

import cPickle
import hashlib
import os

class relex_analysis:
    def __init__(self, options):
        self.relex = relex_analyze()
        self.tagger_class = tagger()
        self.tagger = self.tagger_class.load_tagger()
        self.options = options
        
    def dump_to_file(self, data):
        to_hash = cPickle.dumps(data)
        data_hash = hashlib.sha224(to_hash).hexdigest()
        file = os.path.join('data/','data-%s.txt' % (data_hash))
        
        f_handle = open(file, 'w')
        if isinstance(data, list):
            for lines in data:
                f_handle.write(lines + '\n')
                
        elif isinstance(data, tuple):
            for lines in data:
                if isinstance(lines, list):
                    for rows in lines:
                        f_handle.write(' '.join(rows) + '\n')
                else:
                    f_handle.write(lines + '\n')
                

        f_handle.close()
        
    
    def each_word(self, sentence):
        word_set = []
        if len(sentence[0]) < 0:
            return False
        
        sentence = nltk.word_tokenize(sentence[0])
        tagged = self.tagger.tag(sentence)

        for idx, word_z in enumerate(sentence):
            if not len(word_z) > 1:
                word_container = word(word_z, None, idx)
            else:
                word_container = word(word_z, tagged[idx][1], idx)

            word_set.append(word_container)

        return word_set
            
    def analyze(self, sentences):
        for sentence in sentences:
            ## per sentence instances
            hg = HG(sentence)

            word_set = self.each_word(sentence)
            if not word_set:
                return
            
            features = self.relex.parse_features(sentence)
            frames   = self.relex.parse_frames(sentence)

            ## this will be for analysis
            if False:
                self.dump_to_file((features, frames))

            
            if self.options.graph_tags:
                hg.features_in(features)
            
            if self.options.graph_frame:
                hg.frames_in(frames)

            RE = rule_engine(features, hg.get_hypergraph())
            RE.run_rules()
            
            if self.options.graph:
                hg.analysis()

            
            self.generate_mlnFile(frames, sentence)

    def generate_mlnFile(self, in_data, sentence):
        hashed_sentence = hashlib.sha224(sentence[0]).hexdigest()

        path = os.path.join('data/mln/','mln-%s.db' % (hashed_sentence))
        f_handle = open(path, 'w')
        
        for idx, value in enumerate(sentence[0].split(' ')):
            succ = 'Successors(%d,%d)' % (idx+1,idx)
            word = 'Word("%s", %d)' % (value,idx)
            #tag  = 'Tag(%s:%s,)'
            #debug(succ)
            #debug(word)
            
        

        
