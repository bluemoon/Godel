from structures.containers import universal_sentence
from structures.containers import universal_word
from engines.codecs.relex import relex
from processing.tagger import tagger
from processing.alchemy_api import alchemy_api
from analysis.analysis import relex_analysis
from analysis.hypergraph import HG
from analysis.relex_analysis import relex_analyze


import nltk

class sentence_helper:
    def __init__(self):
        self.tagger = tagger()
        self.tags = []
        
    def tokenize(self, sentence):
        return nltk.word_tokenize(sentence)
    
    def tag(self, tokenized):
        self.tags = self.tagger.tag(tokenized)
        return self.tags

    ## things to be applied to the universal_word
    def universalWord(self, uni_word):
        self.tagToAttribute(uni_word)

    def tagToAttribute(self, uni_word):
        currentTag = self.tags.pop(0)
        partOfSpeech = currentTag[1]
        uni_word.Set('nltk-pos', partOfSpeech)
    
    
class sentence:
    def __init__(self, options):
        self.sentence_frame = []
        self.options = options

        if self.options.engine == 'relex':
            self.codec = relex.relex()
            
        self.relex = relex_analyze()        
        self.analysis = relex_analysis(self.options)
        self.alchemy_api = alchemy_api()
        
        self.helper = sentence_helper()
        self.hg = HG()
        
        
    def process(self, Sentence):
        if not Sentence or len(Sentence) < 2:
            return
        
        word_set = []
        
        tokenized = self.helper.tokenize(Sentence)
        tagged = self.helper.tag(tokenized)
        
        for word in tokenized:
            currentWord = universal_word(word)
            self.helper.universalWord(currentWord)
            word_set.append(currentWord)
            
        universalSentence = universal_sentence(word_set)
        self.sentence_frame.append(universalSentence)

        universalSentence.Set('whole-sentence', Sentence)
        universalSentence.Set('tokenized', tokenized)
        
        processed = self.codec.process(Sentence)
        parsed = self.codec.parse_output(processed)
        
        ## tie the original sentence with the parsed one
        to_analyze = (Sentence, parsed)
        universalSentence.Set('analysis', to_analyze)

        
        #self.alchemy_api.run_all(universalSentence)
        #self.analysis.analyze(universalSentence)
        
        features = self.relex.parse_features(to_analyze)
        universalSentence.Set('features', features)
        ## hypergraph work
        self.hg.sentenceToHG(universalSentence)
        self.hg.features_in(universalSentence)        
        
        
        
