# -*- coding: utf-8 -*-
from collections import namedtuple
from utils.term_colors import *

class universal_container:
    def __getattr__(self, name):
        if self._hasAttr(name):
            return self.attributes[name]
        elif self.__dict__.has_key(name):
            return self.__dict__[name]
    
    def __setattr__(self, name, value):
        if self.attributes == None:
            self.__dict__[name] = value
        else:
            self.attributes[name] = value
        
    def _hasAttr(self, attribute):
        if self.attributes.has_key(attribute):
            return True
        else:
            return False
        
    def Get(self, attribute):
        if self._hasAttr(attribute):
            return self.attributes[attribute]
        else:
            return False
        
    def Set(self, attribute, value):
        self.attributes[attribute] = value
        



class universal_word(universal_container):
    word = None
    attributes = None

    def __init__(self, word):
        self.word = word
        self.attributes = {}
        
        
    def __repr__(self):
        return '<UW word: %s attr: %s>' % (self.word, self.attributes)
        
class universal_sentence(universal_container):
    word_set   = None
    attributes = None

    def __init__(self, word_set):
        self.word_set   = word_set
        self.attributes = {}
        
    def __repr__(self):
        output_string = ''
        
        if self.attributes.has_key('named_entity'):
            named_entity = self.attributes["named_entity"]
            if len(named_entity) > 0:
                named = []
                for named_item in named_entity:
                    temp = named_item.items()[0]
                    temp_string = '%s is a %s' % (temp[0], temp[1])
                    named.append(temp_string)
                
                output_string += "\n\t\t(named entities: %s)" % ', '.join(named)
                
        if self.attributes.has_key('whole_sentence'):
            sentence = self.attributes["whole_sentence"]
            if len(sentence) > 0:
                output_string += "\n\t\t(sentence: %s)" % (sentence)
        
        return "universal_sentence:%s" % (output_string)

class relationships:
    dependencies = None
    frames       = None

    def __init__(self, dependencies, frames):
        self.dependencies = dependencies
        self.frames = frames
        
    def __repr__(self):
        return '<relationships %s>' % (self.dependencies)
