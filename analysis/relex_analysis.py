# -*- coding: utf-8 -*-
from utils.debug import *
import nltk

class relex_analyze:
    def string_before_and_after(self, string, item):
        if item in string:
            idx = string.index(item)
            before = string[:idx]
            after = string[idx+1:]
            return (before, after)
        else:
            return False
        
    def analyze_frames(self, frames):
        lp = nltk.LogicParser(type_check=True)
        val = nltk.Valuation([('P', True), ('Q', True), ('R', False)])
        dom = set([])

        g = nltk.Assignment(dom)
        m = nltk.Model(dom, val)
        print m.evaluate('(P & Q)', g)
        parsed = lp.parse('walk(angus)')

        print parsed.function.type


        for frame in frames:
            debug(frame)
    
    def parse_frames(self, sentence):
        frames_output = []
        frames = sentence[1]
        
        for frame in frames.frames:
            param = None
            ## ^1_Transitive_action:Agent(hehe,you)
            ## ^n_y:z(a,b)
            ## (head, dependent)
            if frame.startswith(';'):
                ## skip it, its a comment
                continue
            left_half, right_half = self.string_before_and_after(frame, ':')

            if '(' in right_half:
                left_p = right_half.index('(')
                
            if ')' in right_half:
                right_p = right_half.index(')')
            
            feature_name = right_half[:left_p]
            parameters = right_half[left_p+1:right_p]
            
            if ',' in parameters:
                left_param, right_param = parameters.split(',')
            else:
                param = parameters
            
            less_sym = left_half[1:]
            
            underscore_split = less_sym.split('_')
            number = underscore_split[:1][0]
            name = '_'.join(underscore_split[1:])
            
            #debug((number, name, feature_name, left_param, right_param))
            if not param:
                frames_output.append((number, name, feature_name, left_param, right_param))
            else:
                frames_output.append((number, name, feature_name, param))
            
        return frames_output
            
    def parse_features(self, sentence):
        feature_output = []
        features = sentence[1]

        if not features:
            return
        
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
            #else:
            #    feature_output.append((feature, parameters))

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
    
