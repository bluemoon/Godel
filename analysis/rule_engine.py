from collections import deque
from utils.debug import *
from rule_parser import parse_file
from structures.atoms import Atoms

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from extensions.guile.guile import VM
from engines.logic.groundings import Groundings

import pprint
import os
import sys


## Frame rules
## Color -> Attribute

class rule_engine:
    def __init__(self):
        ## nltk stemmer
        self.stemmer  = PorterStemmer()

        self.state_stack = []
        self.stack = []

        ## local variables
        self.Grounds = Groundings()
        self.Groundings = {}
        self.Types = {}
        
    def initialize(self, univ_sentence):
        self.tag_stack  = univ_sentence.features
        self.hypergraph = univ_sentence.hypergraph
        
    def interpreter(self, FileList):
        vm = VM('r5rs')
        
        primitive_procedures = [
            ["match-rule?", self.matchRule],
            ["rule-applied", self.rule_applied],
            ["lemma", self.lemma],
            ["in-sentence?", self.inSentence],
            ["make-link", self.addLink],
            ["reset-scope", self.Grounds.variableScope],
            ["ground", self.Grounds.groundVariable],
            ["set-link-type", self.setType],
            ["make-phrase", self.makePhrase],
            ["output-phrase", self.Output],
            ["get-groundings", self.getGroundings],
            ["has-feature?", self.hasFeature],
            ["has-flag?", self.hasFlag],
        ]
        for name, procedure in primitive_procedures:
            vm.define(name, vm.toscheme(procedure))

        for File in FileList:
            vm.load(File)
        
    def run_rules(self):
        files = ['analysis/prep-rules.scm', 'analysis/triple-rules.scm']
        self.interpreter(files)

    def getGroundings(self):
        #debug(self.Groundings)
        pass
        
    def Output(self, Ground1, Ground2, Ground3):
        #self.Groundings = self.output
        ground_1 = None
        ground_2 = None
        ground_3 = None
        
        if self.Grounds.isGround(Ground1) and self.isVariable(Ground1):
            ground_1 = self.Grounds.getGrounding(Ground1)
        elif not self.isVariable(Ground1):
            ground_1 = Ground1
            
        if self.Grounds.isGround(Ground2) and self.isVariable(Ground2):
            ground_2 = self.Grounds.getGrounding(Ground2)
        elif not self.isVariable(Ground2):
            ground_2 = Ground2
            
        if self.Grounds.isGround(Ground3) and self.isVariable(Ground3):
            ground_3 = self.Grounds.getGrounding(Ground3)
        elif not self.isVariable(Ground3):
            ground_3 = Ground3

        
        if ground_1 and ground_2 and ground_3:
            debug([ground_1, ground_2, ground_3], prefix="triple")
            
            self.hypergraph.add_edge(ground_2, ground_3,\
            edge_data=[ground_1], edge_type='triple', with_merge=False)
            
    def rule_applied(self, rule):
        #debug(rule, prefix="rule applied from scheme")
        #if hasattr(self, "output"):
        #    debug(self.output, prefix="Groundings")
        pass
    
    def hasFlag(self, flag, variable):
        ## do we have a given flag
        for x in self.hypergraph.edge_by_type('feature'):            
            head, cur_tag, tail = x
            if cur_tag[0] == flag:
                if self.isVariable(variable) and self.Grounds.isGround(variable):
                    value = self.Grounds.getGrounding(variable)
                else:
                    value = variable
                    
                if head == value:
                    return True

        return False
    
    def hasFeature(self, feature):
        for x in self.hypergraph.edge_by_type('feature'):
            head, cur_tag, tail = x
            if cur_tag == feature:
                return True

        return False
    
    def makePhrase(self, Ground1, Ground2):
        if self.Grounds.isGround(Ground1) and self.Grounds.isGround(Ground2):
            ground_1 = self.Grounds.getGrounding(Ground1)
            ground_2 = self.Grounds.getGrounding(Ground2)
            phrase = '_'.join([ground_1, ground_2])
            self.Grounds.groundVariable('$phrase', phrase)

    def inSentence(self, word):
        pass
    
    def isVariable(self, text):
        ## is it a variable?
        if text.startswith('$'):
            return True
        else:
            return False

    ## Type specifics
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

    ## Grounding specifics
    def compareGround(self, ground, idx):
        if self.Grounds.getGrounding(ground) != self.current[idx]:
            return False
        else:
            return True

    def addLink(self, ground_1, ground_2, type, data=None):
        if self.Grounds.isGround(ground_1) and self.Grounds.isGround(ground_2):
            ground_1 = self.Grounds.getGrounding(ground_1)
            ground_2 = self.Grounds.getGrounding(ground_2)
            
            self.hypergraph.add_edge(ground_1, ground_2, edge_data=[data], edge_type=type, with_merge=False)


    def matchRule(self, rule_set):
        results = []
        state   = None
        stack   = []
        
        for matches in self.match_rule_generator(rule_set):
            ## match to list then append the output
            ## find and match is a generator
            results.append(matches[0])
            state = matches[1]
            
        ## match it outright
        if rule_set == results:
            self.output = matches[1]
            return True

        return False
    
    def replaceOutput(self, ruleOutput, rule):
        if not ruleOutput:
            return False
        
        output = []
        
        for tag_set in rule:            
            replaced = self.replaceVariable(tag_set, self.output)
            output.append(replaced)

        return output
            
    def replaceVariable(self, tag_frame, groundings):
        output = tag_frame
        for x in xrange(len(tag_frame)):
            if self.isVariable(tag_frame[x]):
                if tag_frame[x] in groundings.keys():
                    output[x] = groundings[tag_frame[x]]

        return output
    
    def matchTemplate(self, rule_set, callback):
        output_stack = []
        for key, value in rule_set.items():
            match_rule = callback(value)
            if match_rule[0]:
                output = self.replaceOutput(match_rule, value)
                output_stack.append((key, output))
                
            self.reset()
                
        return output_stack
        
    def matchRuleSet(self, ruleSet):
        output_stack = []
        for key, value in ruleSet.items():
            match_list = self.matchRule(value)
            if match_list:
                output = self.replaceOutput(match_list, value)
                output_stack.append((key, output))
                
            self.reset()
            
        return output_stack
    
    def lemma(self, word, grounding):
        if self.isVariable(word) and self.Grounds.isGround(word):
            groundedWord = self.Grounds.getGrounding(word)
            stemmed = self.stemmer.stem_word(groundedWord)
            self.Grounds.groundVariable(grounding, stemmed)
            
        elif not self.isVariable(word):
            stemmed = self.stemmer.stem_word(word)
            self.Grounds.groundVariable(grounding, stemmed)

    def compareRule(self, tag, var_1, var_2):
        ## check to see if we are ground and it is a var
        if self.isVariable(var_1) and self.Grounds.isGround(var_1):
            out = self.compareGround(var_1, 0)
            if not out:
                return False
            
        ## otherwise we need to ground it
        elif self.isVariable(var_1) and not self.Grounds.isGround(var_1):
            self.Grounds.groundVariable(var_1, self.current[0])
     
        if self.isVariable(var_2) and self.Grounds.isGround(var_2):
            out = self.compareGround(var_2, 2)
            if not out:
                return False
            
        elif self.isVariable(var_2) and not self.Grounds.isGround(var_2):
            self.Grounds.groundVariable(var_2, self.current[2])
            
        if tag == '$prep':
            ## XXX: bad way of doing this
            return True
        
        if self.isVariable(tag) and self.Grounds.isGround(tag):
            self.compareGround(tag, 1)
                
        elif self.isVariable(tag) and not self.Grounds.isGround(tag):
            self.Grounds.groundVariable(tag, self.current[1])
        
        return True
    
    def find_next(self, tag):
        if self.isType(tag):
            tagType = self.getType(tag)
            ## dont play with a loaded gun
            if self.hypergraph.has_edge_type(tagType):
                for x in self.hypergraph.edge_by_type(tagType):
                    head, cur_tag, tail = x
                    edge_data = cur_tag[0]
                    self.Grounds.groundVariable(tag, edge_data)
                    self.current = (head, edge_data, tail)
                    yield (head, edge_data, tail)
            else:
                yield False            
                return
                        
        
        for x in self.hypergraph.edge_by_type('feature'):
            if not isinstance(tag, list):        
                if tag.startswith('$'):
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
                        yield ([tag, var_1, var_2], self.Grounds.getGroundings())

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
                                yield ([tag, var_1, var_2], self.Grounds.getGroundings())

                            else:
                                ## reset the groundings
                                self.Grounds.variableScope()
                    else:
                        self.Grounds.variableScope()
                        



