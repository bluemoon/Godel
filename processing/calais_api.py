from utils.memoize import persistent_memoize

from calais import Calais
from data.calais_key import KEY

class calaisApi:
    def __init__(self):
        self.calais = Calais(KEY, submitter="GodelTest")

    @persistent_memoize
    def calais_run(self, univ_word):
        entities = []
        
        try:
            result = self.calais.analyze(univ_word.whole_sentence)
        except ValueError:
            return
            
        if hasattr(result, "entities"):
            if len(result.entities) > 0:
                for results in result.entities:
                    entities.append(results)

        if len(entities) > 0:
            return entities
        
