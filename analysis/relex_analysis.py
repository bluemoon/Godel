# -*- coding: utf-8 -*-
from utils.debug import *

class relex_analyze:
    def parse_features(self, sentence):
        feature_output = []
        features = sentence[1]
        for deps in features.dependencies:
            deps.replace(' ','')
                        
            left_p  = None
            right_p = None
            comma   = None
            
            if '(' in deps:
                left_p = deps.index('(')
            if ')' in deps:
                right_p = deps.index(')')
            
            feature = deps[:left_p]
            parameters = deps[left_p+1:right_p]
            
            if ',' in parameters:
                comma = parameters.index(',')
                
            left_param = parameters[:comma]
            right_param = parameters[comma+2:]

            feature_output.append((feature, left_param, right_param))

        return feature_output
    
    def seperate_tags(self, tag_set):
        seperate_tags = {
            'tag':        [],
            'gender':     [],
            'POS':        [],
            'flag':       [],
            'inflection': [],
            'HYP':        [],
            'tense':      [],
        }

        tags = ['_subj', '_amod', '_obj', '_to-do', 'for']
        flags = ['DEFINITE-FLAG', 'PRONOUN-FLAG']
        
        for all_tags in tag_set:
            for search_for in tags:
                if search_for == all_tags[0]:
                    seperate_tags['tag'].append(all_tags)
                    
            for flag in flags:
                if flag == all_tags[0]:
                    seperate_tags['flag'].append(all_tags)

            if all_tags[0] == 'inflection-TAG':
                seperate_tags['inflection'].append(all_tags)

            if all_tags[0] == 'pos':
                seperate_tags['POS'].append(all_tags)
                
            if all_tags[0] == 'gender':
                seperate_tags['gender'].append(all_tags)
                
        return seperate_tags
    
