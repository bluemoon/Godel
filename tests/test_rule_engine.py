import unittest
import mox

from analysis.rule_engine import rule_engine
from structures.atoms import Atoms


class testRuleEngine(rule_engine):
    def __init__(self):
        self.tag_stack = []
        self.state_stack = []
        self.stack = []
        self.hypergraph = None
        self.Groundings = {}
        self.Types = {}
        
        self.mox = mox.Mox()
        self.hypergraph = self.mox.CreateMockAnything()
        self.hypergraph.AnyMethod()
        
        
    def tearDown(self):
        self.mox.UnsetStubs()
        
    def test_rule_parser(self):
        self.setType('$prep', 'preposition')
        self.ground_variable('$be', 'be')
        test_rule = [['_obj','$be','$var1'], ['$prep','$var1','$var2']]
        
        self.matchRule(test_rule)

        self.reset()

    def test_prep_rule(self):
        self.setType('$prep', 'preposition')
        self.ground_variable('$be', 'be')
        test_rule = [['$prep','$var1','$var2']]
        
        self.matchRule(test_rule)
        
    
