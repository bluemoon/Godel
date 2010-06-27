from processing.conceptnet.conceptnet import ConceptNet
from processing.conceptnet.divsi import Divsi

class Concepts:
    def __init__(self, options):
        self.options = options
        self.divsi = Divsi()
        self.conceptNet = ConceptNet()
    
    def run(self, universal_word):
        out = []
        
        similarity = self.divsi.concept_similarity(universal_word)
        if similarity:
            out.append(similarity)
        

        concept = self.conceptNet.Connectors(universal_word)
        out.append(concept)

        #concept = self.conceptNet.Surface(universal_word)
        #out.append(concept)

        return out
