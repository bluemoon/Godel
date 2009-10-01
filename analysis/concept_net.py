import os
os.environ['CONCEPTNET_DB_CONFIG'] = os.getcwd() + '/data/conceptnet/db_config.py'

#from csc.util.persist import get_picklecached_thing
from csc.nl import get_nl
from csc.nl.euro import LemmatizedEuroNL
from csc.conceptnet4.models import *
from csc.conceptnet4.analogyspace import conceptnet_2d_from_db

from utils.memoize import persistent_memoize
from utils.debug import *
from utils.class_state import *


class Analogies:
    def __init__(self):
        state = load_state('Analogies')
        if not state[0]:
            self.en_nl = get_nl('en')
            self.normalizer = LemmatizedEuroNL('en')
            self.cnet = conceptnet_2d_from_db('en')
            self.analogyspace = self.cnet.svd(k=100)
            save_state(self, 'Analogies')
        else:
            self = state[1]

    
    def similar(self, tag_set):
        tag_pairs = []
        single_words = []
        
        ## tags are (tag, left, right)
        ## normalize the tag
        for tags in tag_set['tag']:
            stopword_1 = False
            stopword_2 = False
            if self.en_nl.is_stopword(tags[1]):
                stopword_1 = True

            if self.en_nl.is_stopword(tags[2]):
                stopword_2 = True
            
            normal_1 = self.normalizer.normalize(tags[0])
            normal_2 = self.normalizer.normalize(tags[1])
            normal_3 = self.normalizer.normalize(tags[2])

            if stopword_1 and stopword_2:
                ## theres no hope both are stop words
                continue
            elif not stopword_1 and not stopword_2:
                tag_pairs.append((normal_1, normal_2, normal_3))
            elif not stopword_1:
                single_words.append(tags[1])
            elif not stopword_2:
                single_words.append(tags[2])
            
        debug(tag_pairs)
        debug(single_words)
        #analogyspace.weighted_u_vec('tomato')

        '''
        
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
