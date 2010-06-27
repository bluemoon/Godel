from structures.containers import universalConcept
from structures.Graph import Graph
from utils.debug import *
import sys

class ConceptHelper:
    def createConceptMap(self, univ_sentence):
        if not univ_sentence.conceptMap:
            univ_sentence.conceptMap = Graph()
            
    def alchemyNamed(self, univ_sentence):
        entities = univ_sentence.named_entity
        if not univ_sentence.conceptMap:
            self.createConceptMap(univ_sentence)
            
        for entity in entities:
            for key, value in entity.items():
                univ_sentence.conceptMap.add_edge(key, value, ['IsA'])

    def calaisHelper(self, univ_sentence, calais):
        """ [{u'_typeReference': u'http://s.opencalais.com/1/type/em/e/URL',
             u'_type': u'URL', u'name': u'http://85.220.19.235/salrave',
             '__reference': u'http://d.opencalais.com/genericHasher-1/1c690997-12c3-3a2d-bcfa-3da2fa036cf0',
             u'instances': [{u'suffix': u'/', u'prefix': u'IPv4: ', u'detection': u'[IPv4: ]http://85.220.19.235/salrave[/]',
             u'length': 28, u'offset': 6, u'exact': u'http://85.220.19.235/salrave'}], u'relevance': 0.85699999999999998}]

        """
        
        if not calais or len(calais) < 1:
            return
        
        cDict = calais.pop(0)
        defEnc = sys.getdefaultencoding()
        univ_sentence.conceptMap.add_edge(cDict['name'].encode(defEnc), cDict['_type'].encode(defEnc), ['IsA'])
        
        
        
    
        
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
            self.helper.calaisHelper(univ_sentence, calais)
            
        univ_sentence.conceptMap.to_dot_file()

