# -*- coding: utf-8 -*-
from utils.debug import *

from relex_analysis import relex_analyze
from structures.containers import word
from processing.tagger import tagger
from lambda_calc import Lambda_calc

import nltk

import cPickle
import hashlib
import os

class relex_analysis:
    def __init__(self):
        self.relex = relex_analyze()
        self.tagger_class = tagger()
        self.tagger = self.tagger_class.load_tagger()
        
    def each_word(self, sentence):
        word_set = []
        
        assert len(sentence[0]) > 0
        sentence = nltk.word_tokenize(sentence[0])
        tagged = self.tagger.tag(sentence)

        for idx,word_z in enumerate(sentence):
            if not len(word_z) > 1:
                word_container = word(word_z, None, idx)
            else:
                word_container = word(word_z, tagged[idx][1], idx)

            word_set.append(word_container)

        return word_set
            
    def analyze(self, sentences):
        for sentence in sentences:
            cLambda = Lambda_calc()
            
            word_set = self.each_word(sentence)
            cLambda.wordSet_to_lambdaSet(word_set)
            
            features = self.relex.parse_features(sentence)
            frames   = self.relex.parse_frames(sentence)
            seperate_tags = self.relex.seperate_tags(features)

            #self.relex.analyze_frames(frames)
            #self.analogies.similar(seperate_tags)
            cLambda.frames_in(frames)
            cLambda.features_in(features)
            cLambda.bind_set()
            
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
            
        

        
