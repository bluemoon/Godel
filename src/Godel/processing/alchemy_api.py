from libs.AlchemyAPI import AlchemyAPI

from cStringIO import StringIO
import xml.etree.ElementTree 
from xml.etree import ElementTree as ET

class alchemy_api:
    def __init__(self):
        self.alchemy = AlchemyAPI.AlchemyAPI()
        # Load the API key from disk.
        self.alchemy.loadAPIKey("data/api_key.txt")
        
    def language(self, uni_sentence):
        sentence = uni_sentence.whole_sentence
        result = self.alchemy.TextGetLanguage(sentence)
        uni_sentence.Set('alchemy-language', result)

    def keywords(self, uni_sentence):
        sentence = uni_sentence.whole_sentence
        result = self.alchemy.TextGetKeywords(sentence)
        uni_sentence.Set('alchemy-keywords', result)
        xml = StringIO(result)
        #tree = ET.parse(xml)
        xml.seek(0)
        for (event, ele) in ET.iterparse(xml):
            if ele.tag == 'keyword':
                print ele.text.strip()
                ele.clear()
                
    def ranked(self, uni_sentence):
        sentence = uni_sentence.whole_sentence
        result = self.alchemy.TextGetRankedNamedEntities(sentence)
        uni_sentence.Set('alchemy-ranked', result)

    def named(self, uni_sentence):
        sentence = uni_sentence.whole_sentence
        result = self.alchemy.TextGetNamedEntities(sentence)
        
        xml = StringIO(result)
        xml.seek(0)
        
        if uni_sentence.named_entity != []:
            uni_sentence.named_entity = []
            
        for (event, ele) in ET.iterparse(xml):
            if ele.tag == 'entity':
                uni_sentence.named_entity.append({ele.find('text').text:ele.find("type").text})
                ele.clear()
        

    def run_all(self, uni_sentence):
        self.named(uni_sentence)

