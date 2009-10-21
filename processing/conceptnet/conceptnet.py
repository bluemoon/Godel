import os
import sys
sys.path.append(os.getcwd() + '/data/conceptnet/')

from processing.conceptnet.divsi import DivsiHelper
from csc.conceptnet4.models import *
from csc.nl import get_nl


class ConceptNet:
    def __init__(self):
        self.EN = Language.get('en')
        self.helper = DivsiHelper()
        
    def Connectors(self, univ_word):
        Connectors = {}
        for tag in self.helper.interestingTags(univ_word):
            L = tag[0]
            R = tag[1]
            try:
                connector = Assertion.objects.filter(concept1__text=L, concept2__text=R, language=self.EN)
                Connectors[(L,R)] = connector
            except Exception, E:
                print E
                
        return Connectors
