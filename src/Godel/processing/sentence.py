# -*- coding: utf-8 -*-
from structures.containers import universal_sentence
from structures.containers import universal_word

from engines.codecs.relex import relex
from processing.concepts import Concepts
from processing.hypergraph import HG
from processing.sentence_helper import sentence_helper
from analysis.relex_analysis import relex_analyze
from analysis.rule_engine import rule_engine

from utils.debug import *

class sentence:
    """ the main processing class for all of Godel """
    def __init__(self, options):
        self.sentence_frame = []
        self.options = options

        if self.options.engine == 'relex':
            self.codec = relex.relex()
            
        self.relex = relex_analyze()        
        self.rule_engine = rule_engine()
        self.helper = sentence_helper()

        self.concepts = Concepts(self.options)
        
        
    def process(self, Sentence):
        if not Sentence or len(Sentence) < 2:
            return
        
        word_set = []

        self.hg = HG()
        
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

                
        features = self.relex.parse_features(to_analyze)
        if features:
            universalSentence.features = features
            
        ## hypergraph work
        self.hg.sentenceToHG(universalSentence)
        
        
        if features:
            self.hg.features_in(universalSentence) 
        
            hg = self.hg.get_hypergraph()
            self.hg.analysis()
            
            universalSentence.hypergraph = hg
            ## then init the rule engine
            self.rule_engine.initialize(universalSentence)
        
        self.concepts.deriveConcepts(universalSentence)
        

        debug(universalSentence)
        
