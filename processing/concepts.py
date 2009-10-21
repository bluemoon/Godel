from structures.containers import universalConcept

class Concepts:
    def __init__(self, options):
        self.options = options
        
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
        if self.options.concepts:
            concepts = self.concepts.run(univ_sentence)
            debug(concepts)
            
        if self.options.calais:
            calais = self.calais_api.calais_run(univ_sentence.whole_sentence)

        if len(univ_sentence.whole_sentence) > 5 and self.options.alchemy:
            self.alchemy_api.run_all(univ_sentence)

