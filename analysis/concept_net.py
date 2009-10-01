import os
os.environ['CONCEPTNET_DB_CONFIG'] = os.getcwd() + '/data/conceptnet/db_config.py'

#from csc.util.persist import get_picklecached_thing
from csc.nl import get_nl
from csc.nl.euro import LemmatizedEuroNL
from csc.conceptnet4.models import *
from csc.conceptnet4.analogyspace import conceptnet_2d_from_db

from processing.stopwords import is_other_stopword
from utils.memoize import persistent_memoize
from utils.debug import *
from utils.class_state import *

BAD_WORDS = "data/bad_words.txt"

class Analogies:
    def __init__(self):
        self.en_nl = get_nl('en')
        self.normalizer = LemmatizedEuroNL('en')
        self.cnet = conceptnet_2d_from_db('en')
        self.analogyspace = self.cnet.svd(k=100)
        
    def similar(self, tag_set):
        tag_pairs    = []
        single_words = []
        
        ## tags are (tag, left, right)
        ## normalize the tag
        for tags in tag_set['tag']:
            stopword_1 = False
            stopword_2 = False
            
            ## how is also a stopword
            if self.en_nl.is_stopword(tags[1]):
                stopword_1 = True
            if is_other_stopword(tags[1]):
                stopword_1 = True

            if self.en_nl.is_stopword(tags[2]):
                stopword_2 = True
            if is_other_stopword(tags[2]):
                stopword_2 = True

            ## normalize all the words
            normal_1 = self.normalizer.normalize(tags[0])
            normal_2 = self.normalizer.normalize(tags[1])
            normal_3 = self.normalizer.normalize(tags[2])
            
            if stopword_1 and stopword_2:
                ## theres no hope both are stop words
                continue
            elif not stopword_1 and not stopword_2:
                tag_pairs.append((normal_1, normal_2, normal_3))
            elif not stopword_1:
                single_words.append(normal_2)
            elif not stopword_2:
                single_words.append(normal_3)
            
        #debug(tag_pairs)
        #debug(single_words)


        ## analyze single words
        if len(single_words) > 0:
            for word in single_words:
                try:
                    w_vector = self.analogyspace.weighted_u_vec(word)
                    w_v = self.analogyspace.u_dotproducts_with(w_vector)
                    debug('concept: %s top: %s' % (word, w_v.top_items(3)))
                except:
                    f_handle = open(BAD_WORDS, "a")
                    f_handle.write(word + '\n')
                    f_handle.close()

        ## analyze pairs
        if len(tag_pairs) > 0:
            for tag in tag_pairs:
                try:
                    w1_vector = self.analogyspace.weighted_u_vec(tag[1])
                    w2_vector = self.analogyspace.weighted_u_vec(tag[2])
                    #debug(w_vector.top_items())
                    debug('concept %s and %s, simularity %.3f' % (tag[1], tag[2], (w1_vector.hat() * w2_vector.hat())))

                except:
                    pass
                
