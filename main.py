from optparse import OptionParser
from settings import settings
from processing.sentence import sentence
from utils.debug import *
from utils.progress_bar import ProgressBar


import sys

class main:
    def __init__(self):
        self.s = settings()
        
    def option_parser(self):
        self.parser = OptionParser()
        ## set the default options from the cfg file
        default_engine   = self.s.Get('defaults.engine')
        default_source   = self.s.Get('defaults.source')
        default_analysis = self.s.Get('defaults.analysis')
        ## allow the user to over-ride the defaults
        self.parser.add_option("--engine", dest="engine", default=default_engine)
        self.parser.add_option("--source", dest="source", default=default_source)
        self.parser.add_option("--analysis", dest="analysis", default=default_analysis)
        self.parser.add_option("--irc", action="store_true", dest="irc", default=False)
        self.parser.add_option("--without-graph", action="store_false", dest="graph", default=True)
        self.parser.add_option("--with-graph-frame", action="store_true", dest="graph_frame", default=False)
        
        self.parser.add_option("--with-graph-tags", action="store_false", dest="graph_tags", default=True)
        self.parser.add_option("--with-alchemy", action="store_true", dest="alchemy", default=False)
        self.parser.add_option("--with-divsi", action="store_true", dest="divsi", default=False)
        self.parser.add_option("--with-concept-net", action="store_true", dest="concepts", default=False)
        self.parser.add_option("--with-calais", action="store_true", dest="calais", default=False)


        (self.options, self.args) = self.parser.parse_args()
        
    def main(self):
        self.source = None
        self.to_analyze = []
        
        if self.options.irc:
            from utils.irc import irc
            irc()
            return
        
        if self.options.source == 'irc-logs':
            from input.irc_log import irc_logParser

            data_folder = self.s.Get('general.data_directory')
            logParser = irc_logParser()
            self.source = logParser.loadLogs(data_folder + 'logs/2009*', limit=600)

            assert len(self.source) > 0, 'irc source is invalid.'
            
        elif self.options.source == 'tests':
            self.source = ['The quick brown fox jumps over the lazy dog.', 'All cats eat mice.',
                           'The man did not go to the market.', 'what color is the fox?', 'Lisbon is the capital of Portugaul.',
                           'Madrid is a city in Spain.', 'The color of the sky is blue.',
                           'The capital of Germany is Berlin.', 'Pottery is made from clay.', 'chomsky, fetch me two cookies.',
                           'The sky is blue.', 'what color is the sky?', 'chomsky, tell me whats on the new york times today.']


        Sentence = sentence(self.options)
        for current in self.source:
            Sentence.process(current)
            
            
            
if __name__ == '__main__':
    m = main()
    m.option_parser()
    m.main()
