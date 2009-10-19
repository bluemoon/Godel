from optparse import OptionParser
from settings import settings
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
        self.parser.add_option("--without-graph", action="store_false", dest="graph", default=True)
        self.parser.add_option("--with-graph-frame", action="store_true", dest="graph_frame", default=False)
        self.parser.add_option("--with-graph-tags", action="store_false", dest="graph_tags", default=True)
        
        (self.options, self.args) = self.parser.parse_args()
        
    def main(self):
        self.source = None
        self.to_analyze = []
        
        if self.options.source == 'irc-logs':
            from input.irc_log import irc_logParser

            data_folder = self.s.Get('general.data_directory')
            logParser = irc_logParser()
            self.source = logParser.loadLogs(data_folder + 'logs/2009-08-1*', limit=1000)

            assert len(self.source) > 0, 'irc source is invalid.'
            
        elif self.options.source == 'sentence':
            self.source = ['the quick brown fox jumps over the lazy dog.', 'All cats eat mice.',
                           'The man did not go to the market.', 'what color is the fox?', 'Lisbon is the capital of Portugaul.']
            
        if self.options.engine == 'relex':
            from engines.relex import relex
            pb = ProgressBar(max_value=len(self.source), mode='fixed')
            count = 0
            
            r = relex.relex()
            oldprog = str(pb)
            ## then process all of the sentences
            for sentences in self.source:
                pb.increment_amount()
                if oldprog != str(pb):
                    print pb, "\r",
                    sys.stdout.flush()
                    oldprog = str(pb)
                    
                    
                sentence = r.process(sentences)
                #debug(sentence)
                parsed = r.parse_output(sentence)
                ## tie the original sentence with the parsed one
                self.to_analyze.append((sentences, parsed))
                
                count += 1
        print 
                
        if self.options.analysis == 'relex-analysis':
            assert len(self.to_analyze) > 0, 'nothing to analyze.'
            
            from analysis.analysis import relex_analysis
            r = relex_analysis(self.options)
            r.analyze(self.to_analyze)
            
            
            
if __name__ == '__main__':
    m = main()
    m.option_parser()
    m.main()
