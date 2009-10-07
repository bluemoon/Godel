from collections import deque

from utils.debug import *
import nltk

#class NDFSM:
    
    
class Triple:
    last_match = True
    groundings = {}
    current    = None
    hypergraph = None
    rule_fail  = False
    
    stack = []
    output_stack = []
    
    def __init__(self):
        self.groundings = {}
        self.current = None
        self.stack   = []
        self.rule_fail = False
        
    def reset(self):
        ## reset the groundings
        del self.groundings
        self.groundings = {}
        

    def is_ground(self, variable):
        ## is ground
        if self.groundings.has_key(variable):
            return True
        else:
            return False
        
    def is_variable(self, text):
        ## is it a variable?
        if text.startswith('$'):
            return True
        else:
            return False
        
    def compare_ground(self, ground, idx):
        if self.groundings[ground] != self.current[idx]:
            self.last_match = False
            return False
        else:
            return True
        
    def ground_variable(self, variable, ground):
        ## ground a specific variable
        self.groundings[variable] = ground

    def tag_match_list(self, tag_list):
        results = []
        stack   = []
        output  = []
        
        if self.rule_fail:
            return False
        
        for x in self.find_and_match(tag_list):
            results.append(x)

        ## match it outright
        if tag_list == results:
            debug(True)
            return (True, self.groundings)

        else:
            i = 0
            ## if the tags > output no go, misaligned lists
            if len(tag_list) > len(output):
                print len(tag_list)
                print len(output)
                return False
            
            for x in tag_list:
                print x
                print results[i]
                if x == results[i]:
                    output.append(True)
                else:
                    output.append(False)
                    
                i += 1
                
            if False in output:
                return False
            else:
                return True
        return False
        
    def find_and_match(self, tag_list):
        tag_list = deque(tag_list)
        if tag_list:
            popped = tag_list.popleft()
            self.stack.append(popped)
            ## pop off the tag list onto the stack
            tag, var_1, var_2 = self.stack[-1]
            for x in self.find_next(tag):
                ## find our matching tag
                match = self.match_rule(tag, var_1, var_2)
                if match:
                    yield [tag, var_1, var_2, self.groundings]
                    ## run with recursion after yield
                    for x in self.find_and_match(tag_list):
                        tag, var_1, var_2 = tag_list.pop()
                        match = self.match_rule(tag, var_1, var_2)
                        if match:
                            self.stack.append((tag, var_1, var_2))
                            yield [tag, var_1, var_2, self.groundings]
                        else:
                            self.reset()
                            #return 
                else:
                    self.reset()
                    #yield False
                    
                

        
    def find_next(self, tag):
        if tag == '$prep':
            for x in self.hypergraph.edge_by_type('preposition'):
                head, tag, tail = x
                self.current = (head, tag[0], tail)
                yield self.current

        for x in self.hypergraph.edge_by_type('feature'):
            if not isinstance(tag, list):
                if tag.startswith('!') and x[1][0] == tag[1:]:
                    self.rule_fail = True
                    yield False
                
                elif x[1][0] == tag:
                    head, tag, tail = x
                    self.current = (head, tag[0], tail)
                    yield self.current
                
    def all_features(self):
        features = []
        
        for x in self.hypergraph.edge_by_type('feature'):
            features.append(x)
            
        return features
    
    def match_rule(self, tag, var_1, var_2):        
        if self.is_variable(var_1) and self.is_ground(var_1):
            out = self.compare_ground(var_1, 0)
            if not out:
                return False
            
        elif self.is_variable(var_1) and not self.is_ground(var_1):
            self.ground_variable(var_1, self.current[0])
     
        if self.is_variable(var_2) and self.is_ground(var_2):
            out = self.compare_ground(var_2, 2)
            if not out:
                return False
            
        elif self.is_variable(var_2) and not self.is_ground(var_2):
            self.ground_variable(var_2, self.current[2])


        if tag == '$prep':
            return self.last_match
        
        if self.is_variable(tag) and self.is_ground(tag):
            self.compare_ground(tag, 1)
                
        elif self.is_variable(var_2) and not self.is_ground(var_2):
            self.ground_variable(tag, self.current[1])
            
        return True
    

    
class prep_ruleset(Triple):
    def __init__(self, sentence, hg):
        self.output_stack = []
        self.sentence = sentence
        self.hypergraph = hg
        self.groundings = {}

        #self.preposition = True
        
    
    def run_rules(self):
        
        rules = {
            'prep_rule_0' : [['_obj','$be','$var1'], ['$prep','$var1','$var2']],
            'prep_rule_1' : [['_subj','$be','$var1'], ['$prep','$var1','$var2']],
            'prep_rule_2' : [['_predadj','$var1','$var0'], ['$prep','$var1','$var2']],
            'prep_rule_3' : [['_obj','$var1','$var0'], ['$prep','$var1','$var2']],
            'prep_rule_4' : [['_subj','$var1','$var0'], ['$prep','$var1','$var2']],
        }
        for key, value in rules.items():
            self.ground_variable('$be', 'be')
            if self.tag_match_list(value):
                self.output_stack.append(key)
            debug(self.groundings)
            self.reset()
                
        return self.output_stack

    def prep_rule_5(self):
        ## polyword rule
        self.find_next('_subj')
        self.match_rule('_subj','$var1','$var0')
        
        self.find_next('$prep')
        self.match_rule('$prep','$var1', '$var2')
                
        if self.last_match:
            self.output_stack.append('prep_rule_5')
            
                
class triple_ruleset(Triple):
    def __init__(self, tokenized, hypergraph):
        self.hypergraph = hypergraph
        self.sentence = tokenized
        self.groundings = {}
        
        self.output_stack = []

    def run_all(self):
        rules = {
            ## Sentence: "Lisbon is the capital of Portugaul"
            ## _subj(be, Lisbon) ^ _obj(be, capital) ^ of(capital, Portugaul)
            'triple_rule_0' : [['_subj','$be','$var0'],['_obj', '$be','$var1'],['$prep','$var1','$var2']],
            ## Sentence: "The capital of Germany is Berlin"
            ## _subj(be,$var0) ^ _obj(be,$var1) ^ $prep($var0,$var2)
            'triple_rule_1' : [['_subj','$be','$var0'],['_obj', '$be','$var1'],['$prep','$var0','$var2']],
            'triple_rule_2' : [['_predadj','$var1','$var0'],['$prep','$var1','$var2']], 
            'triple_rule_3' : [['!_subj','$x','$y'], ["_obj","$var0","$var1"], ["$prep","$var0","$var2"]],

        }
        for key, value in rules.items():
            self.ground_variable('$be', 'be')
            match_list = self.tag_match_list(value)
            debug(match_list)
            if match_list:
                self.output_stack.append((key, match_list[1]))
                
            self.reset()
                
        return self.output_stack
    




class PrepositionNode:
    head = None
    tail = None
    edge = None

    def __init__(self, head, tail, edge):
        self.head = head
        self.tail = tail
        self.edge = edge
        
    def __repr__(self):
        return '<%s %s %s>' % (self.head, self.edge, self.tail)
        
        
