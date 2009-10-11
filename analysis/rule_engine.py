from collections import deque
from structures.trampoline import trampoline
from utils.debug import *

import clips
import uuid
import os

class rule_engine:
    def __init__(self, hypergraph):
        self.clips = CLIPS()
        
        self.tag_stack   = []
        self.state_stack = []
        
        self.hypergraph  = hypergraph
        
        self.rule_tools = rule_tools(self.hypergraph, self.tag_stack, self.state_stack, self.clips)
        
    def setup_clips(self):
        self.clips.prepare_environment()
        self.setup_callbacks()
        
    def setup_callbacks(self):
        #self.clips.add_callback(self.rule_tools.match, "m", from_class=True)
        self.clips.add_callback(self.rule_tools.set_type, "set-type", from_class=True)
          
    def run_rules(self):
        rule_directory = 'analysis/'
        rule_set = ['prep_rules.clips']#, 'triple_rules.clips']

        env = self.clips.get_enviroment()
        env.Assert('(m _obj word1 word2)')
        
        for rule_file in rule_set:
            rule_f = os.path.join(rule_directory, rule_file)
            f_handle = open(rule_f, 'r')
            text = f_handle.read()   
            env.Build(text)
            f_handle.close()

        env.Run()
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
        self.stack   = []
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

    def set_type(self, variable, type):
        return variable

    def match(self, m1, m2, m3):
        for idx, item in enumerate(self.tag_stack):
            if [m1, m2, m3] == item:
                self.state_stack.append((idx, [m1, m2, m3]))
                return True
            
        return False
    


