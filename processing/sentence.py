# -*- coding: utf-8 -*-
from structures.containers import universal_sentence
from structures.containers import universal_word
from engines.codecs.relex import relex
from processing.tagger import tagger
from processing.alchemy_api import alchemy_api
from analysis.hypergraph import HG
from analysis.relex_analysis import relex_analyze
from analysis.rule_engine import rule_engine

from utils.debug import *

import nltk

class sentence_helper:
    def __init__(self):
        self.tagger = tagger()
        self.tags = []
        
    def tokenize(self, sentence):
        return nltk.word_tokenize(sentence)
    
    def tag(self, tokenized):
        self.tags = self.tagger.tag(tokenized)
        return self.tags

    ## things to be applied to the universal_word
    def universalWord(self, uni_word):
        self.tagToAttribute(uni_word)

    def tagToAttribute(self, uni_word):
        currentTag = self.tags.pop(0)
        partOfSpeech = currentTag[1]
        uni_word.nltk_pos = partOfSpeech
    
    
class sentence:
    def __init__(self, options):
        self.sentence_frame = []
        self.options = options

        if self.options.engine == 'relex':
            self.codec = relex.relex()
            
        self.relex = relex_analyze()        
        self.alchemy_api = alchemy_api()
        
        self.helper = sentence_helper()
        self.hg = HG()
        
        if self.options.divsi:
            from processing.conceptnet.divsi import Divsi
            self.divsi = Divsi()
        
    def process(self, Sentence):
        if not Sentence or len(Sentence) < 2:
            return
        
        word_set = []
        
        tokenized = self.helper.tokenize(Sentence)
        tagged = self.helper.tag(tokenized)

        ## create a container for each word
        for word in tokenized:
            currentWord = universal_word(word)
            self.helper.universalWord(currentWord)
            word_set.append(currentWord)
        
        universalSentence = universal_sentence(word_set)

        ## put the tokens and the sentence as a whole in the
        ## container.
        universalSentence.whole_sentence = Sentence
        universalSentence.tokenized = tokenized
        
        processed = self.codec.process(Sentence)
        parsed = self.codec.parse_output(processed)
        
        ## tie the original sentence with the parsed one
        to_analyze = (Sentence, parsed)
        universalSentence.analysis = to_analyze

        if len(Sentence) > 5 and self.options.alchemy:
            self.alchemy_api.run_all(universalSentence)
        
        features = self.relex.parse_features(to_analyze)
        if features:
            universalSentence.features = features
            
        ## hypergraph work
        self.hg.sentenceToHG(universalSentence)
        
        
        if features:
            self.hg.features_in(universalSentence) 

        hg = self.hg.get_hypergraph()
        universalSentence.hypergraph = hg

        if self.options.divsi and features:
            self.divsi.concept_similarity(universalSentence)

        debug(universalSentence)
        
