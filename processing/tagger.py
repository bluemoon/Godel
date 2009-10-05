from utils.memoize import persistent_memoize

import nltk.corpus, nltk.tag, itertools
from nltk.tag import brill

def backoff_tagger(tagged_sents, tagger_classes, backoff=None):
    if not backoff:
        backoff = tagger_classes[0](tagged_sents)
        del tagger_classes[0]
 
    for cls in tagger_classes:
        tagger = cls(tagged_sents, backoff=backoff)
        backoff = tagger
 
    return backoff

class tagger:
    @persistent_memoize
    def load_tagger(self, sentence_count=20000):
        brownc_sents = nltk.corpus.brown.tagged_sents()[:sentence_count]
        raubt_tagger = backoff_tagger(brownc_sents, [nltk.tag.AffixTagger,
        nltk.tag.UnigramTagger, nltk.tag.BigramTagger, nltk.tag.TrigramTagger])
 
        templates = [
            brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,1)),
            brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (2,2)),
            brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,2)),
            brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,3)),
            brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,1)),
            brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (2,2)),
            brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,2)),
            brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,3)),
            brill.ProximateTokensTemplate(brill.ProximateTagsRule, (-1, -1), (1,1)),
            brill.ProximateTokensTemplate(brill.ProximateWordsRule, (-1, -1), (1,1))
            ]
 
        trainer = brill.FastBrillTaggerTrainer(raubt_tagger, templates)
        braubt_tagger = trainer.train(brownc_sents, max_rules=100, min_score=3)
        return braubt_tagger
 
