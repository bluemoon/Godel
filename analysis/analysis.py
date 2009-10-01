# -*- coding: utf-8 -*-
from utils.debug import *
from concept_net import Analogies
from relex_analysis import relex_analyze

class relex_analysis:
    def __init__(self):
        self.analogies = Analogies()
        self.relex = relex_analyze()
        
    def analyze(self, sentences):
        for sentence in sentences:
            debug(sentence)
            
            features = self.relex.parse_features(sentence)
            frames   = self.relex.parse_frames(sentence)
            seperate_tags = self.relex.seperate_tags(features)

            self.relex.analyze_frames(frames)
            self.analogies.similar(seperate_tags)
                

