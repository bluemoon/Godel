from structures.containers import universalConcept
from structures.atoms import Hypergraph
from utils.debug import *

class ConceptHelper:
    def createConceptMap(self, univ_sentence):
        if not univ_sentence.conceptMap:
            univ_sentence.conceptMap = []
            
    def alchemyNamed(self, univ_sentence):
        entities = univ_sentence.named_entity
        if not univ_sentence.conceptMap:
            self.createConceptMap(univ_sentence)
            
        for entity in entities:
            for key, value in entity.items():
                concept = [key, 'IsA', value]
                uConcept = universalConcept(concept)
                univ_sentence.conceptMap.append(uConcept)
            
        
class Concepts:
    def __init__(self, options):
        self.options = options
        self.helper  = ConceptHelper()
        
        if self.options.concepts:
            from processing.conceptnet.concepts import Concepts
            self.concepts = Concepts(self.options)
            
        if self.options.alchemy:
            from processing.alchemy_api import alchemy_api
            self.alchemy_api = alchemy_api()

        if self.options.calais:
            from processing.calais_api import calaisApi
            self.calais_api = calaisApi()

    def deriveConcepts(self, univ_sentence):
        self.helper.createConceptMap(univ_sentence)
        
        if len(univ_sentence.whole_sentence) > 5 and self.options.alchemy:
            self.alchemy_api.run_all(univ_sentence)
            self.helper.alchemyNamed(univ_sentence)

        if self.options.concepts and univ_sentence.features:
            concepts = self.concepts.run(univ_sentence)
            debug(concepts)
            
        if self.options.calais:
            calais = self.calais_api.calais_run(univ_sentence.whole_sentence)



