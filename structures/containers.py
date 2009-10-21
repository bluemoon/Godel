# -*- coding: utf-8 -*-
#from tagger import braubt_tagger
from collections import namedtuple

class universal_container:
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

    def __repr__(self):
        return repr(self.attributes)

class universal_word(universal_container):
    word = None
    attributes = None
    
    def __init__(self, word):
        self.word = word
        self.attributes = {}
    def __repr__(self):
        return '<word:%s attr:%s>' % (self.word, self.attributes)
        
class universal_sentence(universal_container):
    word_set   = None
    attributes = None
    
    def __init__(self, word_set):
        self.word_set = word_set
        self.attributes = {}




class tag:
    left  = None
    right = None
    tag   = None
    
    def __init__(self, left, right, tag):
        self.left  = left
        self.right = right
        self.tag   = tag

class word:
    word = None
    POS  = None
    idx  = None
    ## stopword true/false
    stopword = None
    
    def __init__(self, word, POS, ID):
        self.word = word
        self.POS  = POS
        self.idx  = ID
        
    def __repr__(self):
        return '<word %s %s %d>' % (self.word, self.POS, self.idx)




class sentence:
    has_left_wall  = None
    has_right_wall = None
    words        = None
    spans        = None
    p_tags       = None
    tags         = None
    sub_links    = None
    atom         = None
    pos          = None
    tag_set      = None
    constituents = None
    diagram      = None
    
    def __init__(self, sentence, normal_words):
        self.words      = sentence[0]
        self.spans      = sentence[1]
        self.p_tags     = sentence[2]
        self.tags       = sentence[3]
        self.sub_links  = sentence[4]
        self.diagram    = sentence[5].split('\n')
        self.tag_set    = []
        
        #self.tagged_words = braubt_tagger.tag(normal_words)
        self.has_right_wall = ('RIGHT-WALL' in sentence[0] and False or True)
        self.has_left_wall  = ('LEFT-WALL'  in sentence[0] and False or True)
        


    def __repr__(self):
        return '<sentence %s>' % (self.words)


class iterative_container:
    def __init__(self):
        self.hash_set = {}
        self.current_number = 1
        
    def add(self, word):
        if word not in self.hash_set:
            self.hash_set[word] = self.current_number
            self.current_number += 1
            
        return self.hash_set[word]


class relationships:
    dependencies = None
    frames       = None

    def __init__(self, dependencies, frames):
        self.dependencies = dependencies
        self.frames = frames
        
    def __repr__(self):
        return '<relationships %s>' % (self.dependencies)
