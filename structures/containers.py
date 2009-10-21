# -*- coding: utf-8 -*-
from collections import namedtuple

class universal_container:
    attributes = {}
    
    def __getattr__(self, name):
        if self._hasAttr(name):
            return self.attributes[name]
    
    def __setattr__(self, name, value):
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
    def __init__(self, word):
        self.word = word
        
    def __repr__(self):
        return '<%s %s>' % (self.word, self.attributes)
        
class universal_sentence(universal_container):
    word_set   = None
    
    def __init__(self, word_set):
        self.word_set = word_set
    def __repr__(self):
        return '<%s %s>' % (self.word_set, self.attributes)

class relationships:
    dependencies = None
    frames       = None

    def __init__(self, dependencies, frames):
        self.dependencies = dependencies
        self.frames = frames
        
    def __repr__(self):
        return '<relationships %s>' % (self.dependencies)
