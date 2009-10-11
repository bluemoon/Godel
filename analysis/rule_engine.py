from collections import deque
from structures.trampoline import trampoline
from utils.debug import *

import os

class rule_engine:
    def __init__(self, tag_stack, hypergraph):
        self.tag_stack   = tag_stack

        self.state_stack = []
        self.stack = []

        self.hypergraph  = hypergraph
        
        self.Groundings = {}
        self.Types = {}

    def run_rules(self):
        pass
    
    def reset(self):
        ## reset the groundings
        del self.Groundings
        self.Groundings = {}
        
    def isGround(self, variable):
        ## is ground
        if self.Groundings.has_key(variable):
            return True
        else:
            return False
        
    def isVariable(self, text):
        ## is it a variable?
        if text.startswith('$'):
            return True
        else:
            return False
        
    def isType(self, variable):
        if self.Types.has_key(variable):
            return True
        else:
            return False
        
    def getType(self, variable):
        if self.isType(variable):
            return self.Types[variable]
        else:
            return False
    
        
    def compare_ground(self, ground, idx):
        if self.Groundings[ground] != self.current[idx]:
            self.last_match = False
            return False
        else:
            return True
        
    def ground_variable(self, variable, ground):
        ## ground a specific variable
        self.Groundings[variable] = ground
    
    
    def find_next(self, tag):
        ## change this to istype and isvariable
        if isType(tag):
            tagType = getType(tag)
            for x in self.hypergraph.edge_by_type(tagType):
                head, tag, tail = x
                edge_data = tag[0]
                
                for preps in prepositions:
                    if edge_data in prepositions:
                        self.preposition = preps
                        yield (head, edge_data, tail)
            
            yield False            
            return
                        
                
        for x in self.hypergraph.edge_by_type('feature'):
            if not isinstance(tag, list):
                if tag.startswith('!') and x[1][0] == tag[1:]:
                    self.rule_fail = True
                    yield False
                    
                elif tag.startswith('$'):
                    head, tag, tail = x
                    self.current = (head, tag[0], tail)
                    yield self.current
                    
                elif x[1][0] == tag:
                    head, tag, tail = x
                    self.current = (head, tag[0], tail)
                    yield self.current
                    
    def match_rule(self, rule_set):
        ## tag list is the list we match to
        ## it is the rule
        rule_set = deque(rule_set)
        
        ## has to be a deque with something in it
        if rule_set:
            popped = rule_set.popleft()
            self.stack.append(popped)
            ## pop off the tag list onto the stack
            tag, var_1, var_2 = self.stack[-1]
            
            ## find the next matching tag
            for x in self.find_next(tag):
                if x:
                    ## find our matching tag
                    match = self.match_rule(tag, var_1, var_2)
                    if match:
                        self.match_stack.append(self.groundings)
                        yield ([tag, var_1, var_2], self.groundings)

                        ## run with recursion after yield
                        for x in self.match_rule(rule_set):
                            ## check for sanity's sake
                            if len(tag_list) > 0:
                                tag, var_1, var_2 = rule_set.popleft()
                            else:
                                return
                            #debug((tag, var_1, var_2))
                            match = self.match_rule(tag, var_1, var_2)
                            #debug(match)
                            if match:
                            ## dump on the stack
                                self.stack.append((tag, var_1, var_2))
                                self.match_stack.append(self.groundings)
                                yield ([tag, var_1, var_2], self.groundings)
                            else:
                                ## reset the groundings
                                self.reset()
                            #return 
                    else:
                        self.reset()
                        

