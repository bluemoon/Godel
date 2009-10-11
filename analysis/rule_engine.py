from collections import deque
from structures.trampoline import trampoline
from utils.debug import *

import os

class rule_engine:
    def __init__(self, tag_stack, hypergraph):
        self.clips = CLIPS()
        self.tag_stack   = tag_stack

        self.state_stack = []
        self.stack = []
        self.hypergraph  = hypergraph
        
        self.rule_tools = rule_tools(self.hypergraph, self.tag_stack, self.state_stack, self.clips)
        
    def match(self):
        ## so we have tags in
        ## [t1, t2, t3, ... tn]
        ## memory which is a clone of tag_stack
        pass

    def reset(self):
        pass
    
    def find_next(self, tag):
        ## change this to istype and isvariable
        if tag == '$prep':
            for x in self.hypergraph.edge_by_type('feature'):
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
                    
    def find_and_match(self, rule_set):
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
                        for x in self.find_and_match(tag_list):
                            ## check for sanity's sake
                            if len(tag_list) > 0:
                                tag, var_1, var_2 = tag_list.popleft()
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
                        

