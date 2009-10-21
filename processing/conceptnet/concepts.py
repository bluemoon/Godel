from processing.conceptnet.divsi import Divsi

class Concepts:
    def __init__(self, options):
        self.options = options
        self.divsi = Divsi()
        
    def run(self, universal_word):
        out = []
        
        similarity = self.divsi.concept_similarity(universal_word)
        out.append(similarity)

        return out
