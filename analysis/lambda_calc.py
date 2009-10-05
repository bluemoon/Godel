# -*- coding: utf-8 -*-

## Cite:
##  Knowledge Representation and Question Answering
##  Marcello Balduccini, Chitta Baral and Yulia Lierler

## Table of symbols:
##  ∀ for all
##  ↔ bilateral
##  λ Lambda   
##
## unbound:
##  λx.plane(x)
##  λx.plane(x) @ Cessna172
##
## bound:
##  plane(Cessna172)
##
## a plane
## λw.λz.∃y.(w @ y ∧ z @ y) @ λx.plane(x) =
## λz.∃y.(λx.plane(x) @ y ∧ z @ y) =
## λz.∃y.(plane(y) ∧ z @ y)
##
##
## λw.λz.∃y.(w @ y ∧ z @ y)
## the representation of “a” is parameterized by
## the class, w, and the property, z, of the object, y:
##
## Transitive:
##  λw.λz.(w @ λx.take(z, x)),
##  where z and x are the placeholders for subject and direct object
##  respectively.
##
## "take a plane":
##   λw.λz.(w @ λx.take(z, x)) @ λw.∃y.(plane(y) ∧ w @ y)
##  assumes NP -> V
##
## "John takes a plane"
## λu.(u @ john) @ λz.(∃y.(plane(y) ∧ take(z, y)))
##
## Action:
##   λu.(u @ bob) @ λx.f(x)
##   λx.f (x) @ bob
##   f(john)
##
##  if f (·) is an action
##   “an unnamed actor x performed action f .”
##
##  ∃y(f lower(y) ∧ take(john, y)).
##
## LLF Sense Based Triple:
##  <base, POS, sense>
## Where:
##   base is the base form of the word
##   POS is the part of speech tag
##   sense is the words classification in wordnet
##
## base_pos_sense(c, a[0] , . . . , a[n] )
##
## Atoms:
## John_NN_(x1), take_VB_11(e1, x1, x2), plane_NN_1(x2)
## x1 denotes the noun (NN) “John”
##
## Possession (POS_SR(X, Y )): X is a possession of Y.
## Agent (AGT_SR(X, Y )): X performs or causes the occurrence of Y.
## Location, Space, Direction (LOC SR(X, Y )): X is the location of Y.
##
## Axioms:
##  ∀x1,x2(in IN (x1 ,x2 ) ↔ into IN (x1,x2)).
##
## FOL output:
## ∃x y z e (p ono(x) ∧ p yoko(x) ∧ r of (z, x)∧
##         n statue(y) ∧ r of (y, z)∧
##         a late(z) ∧ n husband(z) ∧ p lennon(z) ∧ p john(z)∧
##         n event(e) ∧ v unveil(e) ∧ r agent(e, x) ∧ r patient(e, y))
##
## CAUSE(x,y) ^ CAUSE(y,z) -> CAUSE(x,z)
## ACCOMPANIMENT(x,y) -> ACCOMPANIMENT(y,x)
## ACCOMPANIMENT(x,y) ^ LOCATION(y,z) -> LOCATION(x,z)
## INFLUENCE(x,y) ^ CAUSE(y,z) -> INFLUENCE(x,z)
## ISA(x,y) ^ PURPOSE(y,z)  -> PURPOSE(x,z)
## LOCATION(x,y) ^ MAKEPRODUCE(y,z) -> PURPOSE(x,z)
##
##
## Relex Tags
## _%quantity all = ∀∃(x)
## Relex frames

## (Negation, Theme, x, y) = !{x, y}
## (Temporal_colocation, Event, x, y) -> Happened(x, y)
## (Motion, Goal, x, y) ^ (Self_motion, Theme, x, z) -> Self_Action(x, y, z)
## (Becoming, Entity, x, y) -> Action()
## (Motion, Goal, x, y)
## (Self_motion, Theme, x, y)
## (Self_motion, Goal, x, y) -> Self_goal(x,y)
## (Purpose, Agent, x, y)
## (Possibilites, Event, hyp, x)

import cPickle
import nltk
from utils.debug import *
from utils.list import list_functions

class Lambda_calc:
    def __init__(self):
        self.bindings = Bindings()
        self.list_functions = list_functions()
        
        self.lambda_set = []
        self.leftover_frames = []
        self.features = []
        
    def get_word_in_set(self, word):
        for idx,L in enumerate(self.lambda_set):
            if word == L.word:
                ## wtf do we do if we have same word in the same sentence?
                return (idx, L)

                
    def wordSet_to_lambdaSet(self, word_set):
        for word in word_set:
            LW = LambdaWord(word.word)
            LW.POS = word.POS
            LW.idx = word.idx
            
            self.lambda_set.append(LW)
            debug(LW)

    def features_in(self, features):
        debug(features)
        
    def frames_in(self, frames):
        frames = self.list_functions.uniqify(frames)
    
        for frame in frames:
            f_dict = {}
            debug(frame)
            
            f_dict['number']      = frame[0]
            f_dict['concept']     = frame[1]
            f_dict['sub_concept'] = frame[2]
            f_dict['word']        = frame[3]
            f_dict['refers']      = frame[4]

            word = self.get_word_in_set(f_dict['word'])
            refers = self.get_word_in_set(f_dict['refers'])
            
            if refers == None:
                continue
            
            refers[1].referred_by.append(f_dict)

            if word == None:
                self.leftover_frames.append(f_dict)
                continue

            word[1].frames.append(f_dict)
            word[1].bound_links.append(f_dict)

            

        ## debug(self.leftover_frames)

    def wordnet_entry(self, word):
        try:
            entry = nltk.wordnet.N[word]
        except:
            entry = False

        return entry

    def bind_set(self):
        for lambda_item in self.lambda_set:
            each_lambda = []
            for frame in lambda_item.frames:
                each_lambda.append((frame['concept'], frame['sub_concept'], frame['refers']))


            self.bindings.build_binding((lambda_item, each_lambda))

            
class Bindings:
    def __init__(self):
        self.list_functions = list_functions()

        self.bindings = []
        
    def build_binding(self, word_data):
        if not word_data[1]:
            return
        
        referrers = []
        
        lambda_item, referents = word_data
        debug(lambda_item.word)
        debug(lambda_item.POS)
        debug(referents)


        for r in referents:
            ref_type = '_'.join([r[0],r[1]])
            
            referrers.append(r[2])
            self.bindings.append(binding(r[1],lambda_item.word))
            #if ref_type == 'Purpose_Attribute':
            #    self.bindings.append(binding(lambda_item.word, r[2]))
            #    debug(self.bindings)

            #if ref_type == 'Building_Agent':
            #    ## λu.(u @ <ref>) @ λx.<word>(x)
            #    self.bindings.append(binding(lambda_item.word, r[2]))
            #    debug(self.bindings)

        referrers = self.list_functions.uniqify(referrers)
        to_print = ', '.join(referrers)
        debug_string =  'Predicate logic: %s_%s(%s)' % (lambda_item.word, lambda_item.POS, to_print)
        
        debug(debug_string)
        #debug_string = 'Boxer Style: %s(%d)' % (lambda_item.idx, )

        self.bindings = self.list_functions.uniqify(self.bindings)
        debug(self.bindings)



##### CONTAINERS #####
class binding:
    word  = None
    binds = None
    
    def __init__(self, word, binds):
        self.word = word
        self.binds = binds
    def __repr__(self):
        return '<binding "%s" binds "%s">' % (self.word, self.binds)
        

class LambdaWord:
    ## bound will be bound or not bound
    ## with True/False respectively
    bound = None
    bound_links = None
    
    word = None
    POS = None
    idx = None

    frames = None
    referred_by = None
    
    def __init__(self, word):
        self.word = word
        self.bound = False
        self.frames = []
        self.referred_by = []
        self.bound_links = []
        
    def __repr__(self):
        if not self.bound:
            return "lambda x.%s(x)" % (self.word)
        else:
            return self.word
        
   
        
        
        
        
    
