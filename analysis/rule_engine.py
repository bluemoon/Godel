from collections import deque
from structures.trampoline import trampoline
from utils.debug import *

import clips
import uuid
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
                                self.reset()
                            #return 
                    else:
                        self.reset()
                        
    def setup_clips(self):
        self.clips.prepare_environment()
        self.setup_callbacks()
        
    def setup_callbacks(self):
        self.clips.add_callback(self.rule_tools.match, "m", from_class=True)
        self.clips.add_callback(self.rule_tools.set_type, "set-type", from_class=True)
        
    def get_rule(self):
        rule_directory = 'analysis/'
        rule_set = ['prep_rules.clips']
        env = self.clips.get_enviroment()
        
        for rule_file in rule_set:
            ## load up the file
            rule_f = os.path.join(rule_directory, rule_file)
            f_handle = open(rule_f, 'r')
            text = f_handle.read()   
            ## then build the ruleset
            env.Build(text)
            ## close the file
            f_handle.close()

        
            
    def run_rules(self):
        env = self.clips.get_enviroment()
        self.get_rule()
        
        ## we need to set the first word here...
        ## env.Assert('(m _obj word1 word2)')
        for tag in self.rule_tools.tag_next():
            self.state_stack.append(tag)
            

        ## run our enviroment
        env.Run()
        
        ## purely for debugging
        env.PrintFacts()
        env.PrintRules()

            
        #print env.Eval('(set-type $prep preposition)')
	#print env.Eval('(m $prep $var1 $var2)')
        

class CLIPS:
    def __init__(self):
        # the following dictionary will contain the environment specific functions
        self.ENV_SPECIFIC_FUNCTIONS = {}
        self.enviroment = clips.Environment()
        clips.RegisterPythonFunction(self.enviroment_callback, 'env-call-specific-func')
        clips.DebugConfig.ActivationsWatched = True
        
    def get_enviroment(self):
        return self.enviroment
    
    def enviroment_id(self):
        # a Python function to create a simple Environment identifier: the initial
        #  "eid-" prefix is just to ensure that the resulting string can be a SYMBOL
        return clips.Symbol("eid-" + str(uuid.uuid1()))
 

    def enviroment_callback(self, enviroment_id, funcname, *args):
        # ...and this wrapper calls in turn the functions associated with certain
        #  names for each environment
        f = self.ENV_SPECIFIC_FUNCTIONS[enviroment_id][funcname]
        return f(*args)

    def prepare_environment(self):
        # now we need some helpers to make it easier to set up the environment and
        #  the map of environment specific functions
        eid = self.enviroment_id()
        self.ENV_SPECIFIC_FUNCTIONS[eid] = {}   # a map of functions
        self.enviroment.Identifier = eid   # so that we can always get it back
        return eid
 
    def add_callback(self, func, funcname=None, from_class=False):
        eid = self.enviroment.Identifier
        if funcname is None:
            funcname = func.__name__    # if needed
            
        self.ENV_SPECIFIC_FUNCTIONS[eid][funcname] = func
        less_count = (from_class != False and 1 or 0)
        num_args = func.func_code.co_argcount - less_count
        
        seq_args = " ".join(['?a%s' % x for x in range(num_args)])
        self.enviroment.BuildFunction(
            funcname,
            seq_args,
            "(return (python-call env-call-specific-func %s %s %s))" % (
                eid, funcname, seq_args))
        


class rule_tools:
    def __init__(self, hypergraph, tag_stack, state_stack, clips):
        self.groundings = {}
        self.stack = []
        self.clips = clips
        self.types = {}
        
        self.tag_stack   = tag_stack
        self.state_stack = state_stack

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

    def tag_next(self):
        for idx,tag in enumerate(self.tag_stack):
            yield (idx, tag)
            
    def set_type(self, variable, type):
        return variable

    def match(self, m1, m2, m3):
        ## i dont know how i should do the searching with clips
        ## maybe something like match rule then use the python function
        ## to generate the next word assertion the problem is that i dont
        ## know what the next one will be

        ## so the first one will be <tag, word1, word2>
        ## but then i dont know what the next one will be
        ## i can easily find n+1
        enviroment = self.clips.get_enviroment()
        
        for idx, item in enumerate(self.tag_stack):
            if [m1, m2, m3] == item:
                self.state_stack.append((idx, [m1, m2, m3]))
                enviroment.Assert('(m %s %s %s)' % (m1, m2, m3))
                return True
            
        return False
    


