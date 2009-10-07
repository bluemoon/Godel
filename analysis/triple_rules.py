from utils.debug import *
import nltk

## make-prep-phrase
##  _obj(be,$var1) ^ $prep($var1,$var2) 
##  _subj(be,$var1) ^ $prep($var1,$var2) 
##  _predadj($var1,$var0) ^ $prep($var1,$var2)
##  _obj($var1,$var0) ^ $prep($var1,$var2)

## prep-rule-4
##  _subj($var1,$var0)

## make-polyword-phrase
##  _subj($pwi,$var1)

## subject
##  _subj($verb,$qVar) ^ _obj($verb, obj-var)
##  _obj($ans-verb, obj-var) ^ _subj($ans-verb, answer_subj)

## triple-rule-0
##  _subj(be, Lisbon) ^ _obj(be, capital) ^ of(capital, Portugaul)
##  var0=Lisbon, var1=capital var2=Portugaul

## triple-rule-1
##  _subj(be,$var0) ^ _obj(be,$var1) ^ $prep($var0,$var2)

## truth-assertion-rule
##  _subj(make, John) ^ _obj(make, fun) ^ of(fun, Sarah) ^ !flag(hyp, $verb) ^ !flag(truth-query ,$verb)

prepositions = [
    'aboard',
    'about',
    'above',
    'across',
    'after',
    'against',
    'along',
    'alongside',
    'amid',
    'amidst',
    'among',
    'amongst',
    'around',
    'as',
    'aside',
    'at',
    'athwart',
    'atop',
    'barring',
    'before',
    'behind',
    'below',
    'beneath',
    'beside',
    'besides',
    'between',
    'beyond',
    'but',
    'by',
    'circa',
    'concerning',
    'despite',
    'down',
    'during',
    'except',
    'failing',
    'following',
    'for',
    'from',
    'in',
    'inside',
    'into',
    'like',
    'minus',
    'near',
    'next',
    'notwithstanding',
    'of',
    'off',
    'on',
    'onto',
    'opposite',
    'out',
    'outside',
    'over',
    'pace',
    'past',
    'per',
    'plus',
    'regarding',
    'round',
    'save',
    'since',
    'than',
    'through',
    'throughout',
    'till',
    'times',
    'to',
    'toward',
    'towards',
    'under',
    'underneath',
    'unlike',
    'until',
    'up',
    'upon',
    'versus',
    'via',
    'with',
    'within',
    'without',
    'worth',
    #
    # two-word preps
    #
    'according_to',
    'ahead_of',
    'aside_from',
    'because_of',
    'close_to',
    'due_to',
    'except_for',
    'far_from',
    'in_to',
    'inside_of',
    'instead_of',
    'near_to',
    'next_to',
    'on_to',
    'out_from',
    'out_of',
    'outside_of',
    'owing_to',
    'prior_to',
    'pursuant_to',
    'regardless_of',
    'subsequent_to',
    'that_of',
    #
    # three-word preps
    #
    'as_far_as',
    'as_well_as',
    'by_means_of',
    'in_accordance_with',
    'in_addition_to',
    'in_case_of',
    'in_front_of',
    'in_lieu_of',
    'in_place_of',
    'in_spite_of',
    'on_account_of',
    'on_behalf_of',
    'on_top_of',
    'with_regard_to',
    #
    # postpositions
    #
    # five years ago
    'ago',
    'this apart',
    'apart',
    'away',
    'hence',
]

    
class Triple:
    last_match = True
    groundings = {}
    current    = None
    hypergraph = None
    preposition = False
    
    def __init__(self):
        self.groundings = {}
        self.current = None
        self.stack   = []
        self.last_match = True
        
    def reset(self):
        self.last_match = True
        del self.groundings
        self.groundings = {}
        
    def in_sentence(self, word):
        pass

    def is_ground(self, variable):
        if self.groundings.has_key(variable):
            return True
        else:
            return False
        
    def is_variable(self, text):
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
        
    def ground_tag(self, tag, value):
        if self.is_variable(tag) and self.is_ground(tag):
            return True
        elif not self.is_ground(tag):
            self.ground_variable(tag, value)
            return
        else:
            return False
            
    def ground_variable(self, variable, ground):
        self.groundings[variable] = ground  
            
    def find_next(self, tag):
        if tag == '$prep':
            for x in self.hypergraph.edge_by_type('preposition'):
                head, tag, tail = x
                self.current = (head, tag[0], tail)
                yield self.current
                


        for x in self.hypergraph.edge_by_type('feature'):
            if x[1][0] == tag:
                head, tag, tail = x 
                self.current = (head, tag[0], tail)
                yield (head, tag[0], tail)
                
    
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
        
    def PairUp(self):
        pass
    
    def run_rules(self):
        self.prep_rule_0()
        self.reset()
        self.prep_rule_1()
        self.reset()
        self.prep_rule_2()
        self.reset()
        self.prep_rule_3()
        self.reset()
        self.prep_rule_4()
        self.reset()
        
        return self.output_stack

    def prep_rule_0(self):
        found_match = False
        ## _obj(be, $var1)
        for x in self.find_next('_obj'):
            match1 = self.match_rule('_obj','be','$var1')
            for y in self.find_next('$prep'):
                match2 = self.match_rule('$prep','$var1', '$var2')
                if match1 and match2:
                    found_match = True
                    break
        
        if found_match:
            self.output_stack.append('prep_rule_0')
    
    def prep_rule_1(self):
        found_match = False
        ## _obj(be, $var1)
        
        for x in self.find_next('_subj'):
            match1 = self.match_rule('_subj','be','$var1')
            for y in self.find_next('$prep'):
                match2 = self.match_rule('$prep','$var1', '$var2')
                if match1 and match2:
                    found_match = True
                
            self.reset()
                    
        if found_match:
            self.output_stack.append('prep_rule_1')

        
    def prep_rule_2(self):
        found_match = False
        for x in self.find_next('_predadj'):
            match1 = self.match_rule('_predadj','$var1','$var0')
            for y in self.find_next('$prep'):
                match2 = self.match_rule('$prep','$var1', '$var2')
                if match1 and match2:
                    found_match = True
        
        
        if found_match:
            self.output_stack.append('prep_rule_2')
            
    def prep_rule_3(self):
        found_match = False
        for x in self.find_next('_obj'):
            match1 = self.match_rule('_obj','$var1','$var0')
            for y in self.find_next('$prep'):
                match2 = self.match_rule('$prep','$var1', '$var2')
                if match1 and match2:
                    found_match = True
        
        if found_match:
            self.output_stack.append('prep_rule_3')

    def prep_rule_4(self):
        found_match = False
        for x in self.find_next('_subj'):
            match1 = self.match_rule('_subj','$var1','$var0')
            for y in self.find_next('$prep'):
                match2 = self.match_rule('$prep','$var1', '$var2')
                if match1 and match2:
                    found_match = True
        
        if found_match:
            self.output_stack.append('prep_rule_4')

    
    def prep_rule_5(self):
        ## polyword rule
        self.find_next('_subj')
        self.match_rule('_subj','$var1','$var0')
        
        self.find_next('$prep')
        self.match_rule('$prep','$var1', '$var2')
                
        if self.last_match:
            self.output_stack.append('prep_rule_5')
                
class triple_ruleset(Triple):
    def __init__(self, tag_set, sentence):
        self.frame_set = tag_set
        self.sentence = sentence
        
        self.output_stack = []

    def run_all(self):
        #debug(self.frame_set)
        self.triple_rule_0()
        self.reset()
        self.triple_rule_1()
        self.reset()
        self.triple_rule_2()
        
        return self.output_stack
    
            
    def triple_rule_0(self):
        ## Sentence: "Lisbon is the capital of Portugaul"
        ## _subj(be, Lisbon) ^ _obj(be, capital) ^ of(capital, Portugaul)
        
        self.find_next('_subj')
        self.ground_variable('$be', 'be')
        self.match_rule('_subj','$be','$var0')
        
        self.find_next('_obj')
        self.match_rule('_obj','$be','$var1')

        self.find_next('$prep')
        self.match_rule('$prep','$var1','$var2')
        
        if not self.last_match:
            self.output_stack.append((False, 'triple_rule_0'))
        else:
            self.output_stack.append((True,  'triple_rule_0'))
        
    def triple_rule_1(self):
        ## Sentence: "The capital of Germany is Berlin"
        ## _subj(be,$var0) ^ _obj(be,$var1) ^ $prep($var0,$var2)
        self.find_next('_subj')
        self.ground_variable('$be', 'be')
        self.match_rule('_subj','$be','$var0')

        self.find_next('_obj')
        self.match_rule('_obj','$be','$var1')

        #self.find_next('$prep')
        #self.match_rule('$prep','$var0','$var2')

        if not self.last_match:
            self.output_stack.append((False, 'triple_rule_1'))
        else:
            self.output_stack.append((True,  'triple_rule_1'))
        
        
    def triple_rule_2(self):
        ## _predadj($var1,$var0) ^ $prep($var1,$var2)
        self.find_next('_predadj')
        self.match_rule('_predadj', '$var1', '$var2')

        self.find_next('$prep')
        self.match_rule('$prep', '$var1', '$var2')
        
        if not self.last_match:
            self.output_stack.append((False, 'triple_rule_2'))
        else:
            self.output_stack.append((True,  'triple_rule_2'))


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
        
        
