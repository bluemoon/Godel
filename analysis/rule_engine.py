from collections import deque
from utils.debug import *
from rule_parser import parse_file

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer


import os

class rule_engine:
    def __init__(self, tag_stack, hypergraph):
        self.tag_stack   = tag_stack

        self.lemma = WordNetLemmatizer()
        ## .lemmatize('cars')
        self.porter  = PorterStemmer()
        ## p.stem('running')


        self.state_stack = []
        self.stack = []

        self.hypergraph = hypergraph
        
        self.Groundings = {}
        self.Types = {}
        
    def run_rules(self):
        #self.parse_rulefile('')
        ## self.test_rule_parser()
        ## self.test_prep_rule()
        self.setType('$prep', 'preposition')
        self.setType('$in_sent', 'sentence')
        
        prep = prepRules(self.tag_stack, self.hypergraph)
        triples = tripleRules(self.tag_stack, self.hypergraph)
        
        debug(prep.run_rules())
        debug(triples.run_rules())
        
    def test_rule_parser(self):

        self.ground_variable('$be', 'be')
        test_rule = [['_obj','$be','$var1'], ['$prep','$var1','$var2']]
        
        self.matchRule(test_rule)

        self.reset()

    def test_prep_rule(self):
        self.setType('$prep', 'preposition')
        self.ground_variable('$be', 'be')
        test_rule = [['$prep','$var1','$var2']]
        
        self.matchRule(test_rule)

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
    
    def setType(self, variable, Type):
        self.Types[variable] = Type
        
    def compareGround(self, ground, idx):
        if self.Groundings[ground] != self.current[idx]:
            return False
        else:
            return True
        
    def ground_variable(self, variable, ground):
        ## ground a specific variable
        self.Groundings[variable] = ground

    def makeLink(self, tag_set):
        self.hypergraph.add_edge(tag[1], tag[2], edge_data=[], edge_type='preposition-link', with_merge=False)
        
    def matchRule(self, rule_set):
        results = []
        state   = None
        stack   = []
        output  = []
        
        for matches in self.match_rule_generator(rule_set):
            ## match to list then append the output
            ## find and match is a generator
            results.append(matches[0])
            state = matches[1]
            
        debug(rule_set)
        debug(results)
        debug(state)
        
        ## match it outright
        if rule_set == results:
            return (True, state)
            
        else:
            i = 0
            ## if the tags > output no go, misaligned lists
            if len(rule_set) > len(output):
                return False
            
            ## FIXME: i need to fix this, so it works/doesnt suck
            for x in tag_list:
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
    
    def replaceOutput(self, ruleOutput, rule):
        if not ruleOutput:
            return False
        
        output = []
        
        for tag_set in rule:            
            replaced = self.replaceVariable(tag_set, ruleOutput[1])
            output.append(replaced)

        return output
            
    def replaceVariable(self, tag_frame, groundings):
        output = tag_frame
        for x in xrange(len(tag_frame)):
            if self.isVariable(tag_frame[x]):
                if tag_frame[x] in groundings.keys():
                    output[x] = groundings[tag_frame[x]]

        return output

    def matchRuleSet(self, ruleSet):
        output_stack = []
        for key, value in ruleSet.items():
            self.ground_variable('$be', 'be')
            
            match_list = self.matchRule(value)
            if match_list:
                output = self.replaceOutput(match_list, value)
                output_stack.append((key, output))
                
            self.reset()
                
        return output_stack
    
    def compareRule(self, tag, var_1, var_2):
        #debug([tag, var_1, var_2])
        ## check to see if we are ground and it is a var
        if self.isVariable(var_1) and self.isGround(var_1):
            out = self.compareGround(var_1, 0)
            if not out:
                return False
            
        ## otherwise we need to ground it
        elif self.isVariable(var_1) and not self.isGround(var_1):
            self.ground_variable(var_1, self.current[0])
     
        if self.isVariable(var_2) and self.isGround(var_2):
            out = self.compareGround(var_2, 2)
            if not out:
                return False
            
        elif self.isVariable(var_2) and not self.isGround(var_2):
            self.ground_variable(var_2, self.current[2])
            
        if tag == '$prep':
            ## XXX: bad way of doing this
            return True
        
        if self.isVariable(tag) and self.isGround(tag):
            self.compareGround(tag, 1)
                
        elif self.isVariable(var_2) and not self.isGround(var_2):
            self.ground_variable(tag, self.current[1])
        
        return True
    
    def find_next(self, tag):
        debug(tag)
        if self.isType(tag):
            tagType = self.getType(tag)
            debug(tagType)
            ## dont play with a loaded gun
            if self.hypergraph.has_edge_type(tagType):
                for x in self.hypergraph.edge_by_type(tagType):
                    head, cur_tag, tail = x
                    edge_data = cur_tag[0]
                    debug(tag)
                    self.ground_variable(tag, edge_data)
                    self.current = (head, edge_data, tail)
                    yield (head, edge_data, tail)
            else:
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
                    
    def match_rule_generator(self, rule_set):
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
                    match = self.compareRule(tag, var_1, var_2)
                    if match:
                        ## self.match_stack.append(self.groundings)
                        yield ([tag, var_1, var_2], self.Groundings)

                        ## run with recursion after yield
                        for x in self.match_rule_generator(rule_set):
                            ## check for sanity's sake
                            if len(rule_set) > 0:
                                tag, var_1, var_2 = rule_set.popleft()
                            else:
                                return
                            
                            #debug((tag, var_1, var_2))
                            match = self.compareRule(tag, var_1, var_2)
                            #debug(match)
                            if match:
                            ## dump on the stack
                                self.stack.append((tag, var_1, var_2))
                                ## self.match_stack.append(self.groundings)
                                yield ([tag, var_1, var_2], self.Groundings)
                            else:
                                ## reset the groundings
                                self.reset()
                            #return 
                    else:
                        self.reset()
                        


class prepRules(rule_engine):
    def prep_rule_0(self):
        self.ground_variable('$be', 'be')
        match = matchRule([['_obj','$be','$var1'], ['$prep','$var1','$var2']])
            
        
        
    def run_rules(self):
        rules = {
            'prep_rule_0' : [['_obj','$be','$var1'], ['$prep','$var1','$var2']],
            'prep_rule_1' : [['_subj','$be','$var1'], ['$prep','$var1','$var2']],
            'prep_rule_2' : [['_predadj','$var1','$var0'], ['$prep','$var1','$var2']],
            'prep_rule_3' : [['_obj','$var1','$var0'], ['$prep','$var1','$var2']],
            'prep_rule_4' : [['_subj','$var1','$var0'], ['$prep','$var1','$var2']],
        }
        output = self.matchRuleSet(rules)
        ## self.hypergraph.delete_edge_type('preposition')
        if output:
            for tag in output[0][1]:
                if tag[0] == '$prep':
                    self.hypergraph.add_edge(tag[1], tag[2], edge_data=[], edge_type='preposition-link', with_merge=False)

        self.hypergraph.to_dot_file(primary_type='sentence')
        return output
    
class tripleRules(rule_engine):
    def triple_rule_0(self):
        rule = [['_subj','$be','$var0'],['_obj', '$be','$var1'],['$prep','$var1','$var2']]
        match = self.matchRule(rule)
        if match:
            pass
        
    def run_rules(self):
        rules = {
            ## Sentence: "Lisbon is the capital of Portugaul"
            ## _subj(be, Lisbon) ^ _obj(be, capital) ^ of(capital, Portugaul)
            'triple_rule_0' : [['_subj','$be','$var0'],['_obj', '$be','$var1'],['$prep','$var1','$var2']],
            ## Sentence: "The capital of Germany is Berlin"
            ## _subj(be,$var0) ^ _obj(be,$var1) ^ $prep($var0,$var2)
            'triple_rule_1' : [['_subj','$be','$var0'],['_obj', '$be','$var1'],['$prep','$var0','$var2']],
            'triple_rule_2' : [['_predadj','$var1','$var0'],['$prep','$var1','$var2']], 
            'triple_rule_3' : [['!_subj','$x','$y'], ["_obj","$var0","$var1"], ["$prep","$var0","$var2"]],
            'triple_rule_4' : [['_obj','$in_sent','$var1'], ["_iobj","$in_sent","$var2"]],
            'triple_rule_6' : [["_subj","$be","$var1"], ["_obj","$be","$var2"]],
        }
        output = self.matchRuleSet(rules)
        return output
    
