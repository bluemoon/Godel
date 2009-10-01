import os
os.environ['CONCEPTNET_DB_CONFIG'] = os.getcwd() + '/data/conceptnet/db_config.py'

#from csc.util.persist import get_picklecached_thing
#from csc.nl import get_nl
#from csc.nl.euro import LemmatizedEuroNL
#from csc.conceptnet4.models import *
#from csc.conceptnet4.analogyspace import conceptnet_2d_from_db
#from csc.divisi.flavors import ConceptByFeatureMatrix

from utils.debug import *

class Analogies:
    def __init__(self):
        #self.en_nl = get_nl('en')
        #self.normalizer = LemmatizedEuroNL('en')
        #self.cnet = conceptnet_2d_from_db('en')
        #self.analogyspace = self.cnet.svd(k=100)
        pass
    
    def similar(self, word_set):
        pass
        '''
        for words in word_container.tagged_words:
            normal = self.normalizer.normalize(words[0])
            untagged.append(normal)

        whole_sentence = ' '.join(untagged)
        lemma_d = self.en_nl.lemma_split(whole_sentence)
        print lemma_d
        lemma = lemma_d[0].split(' ')
        
        for x in lemma:
            try:
                debug(x)
                obj = self.analogyspace.weighted_u[x, :]
                last.append(obj)
                
                if len(last) > 1:
                    print obj.hat() * last[-2].hat()
                
                #cur = self.analogyspace.u_dotproducts_with(obj)
                #print cur.top_items()
                #analogyspace.weighted_v.label_list(0)[:10]

            except Exception, E:
                print E
                

        '''
