from optparse import OptionParser
from settings import settings

class main:
    def __init__(self):
        self.s = settings()
        self.settings = self.s.settings()
        
    def option_parser(self):
        self.parser = OptionParser()
        
        default_engine   = self.s.Get('defaults.engine')
        default_source   = self.s.Get('defaults.source')
        default_analysis = self.s.Get('defaults.analysis')
        
        self.parser.add_option("--engine", dest="engine", default=default_engine)
        self.parser.add_option("--source", dest="source", default=default_source)
        self.parser.add_option("--analysis", dest="analysis", default=default_analysis)
        
        (self.options, self.args) = self.parser.parse_args()
        
    def main(self):
        self.source = None
        self.to_analyze = None
        
        if self.options.source == 'irc-logs':
            from input.irc_log import irc_logParser
            
            logParser = irc_logParser()
            self.source = logParser.loadLogs(DATA_FOLDER + 'logs/2009-08-1*', limit=200)

            assert len(self.source) > 0, 'irc source is invalid.'

        if self.options.engine == 'relex':
            from engines.relex import relex
            r = relex.relex()
            ## then process all of the sentences
            for sentences in self.source:
                sentence = r.process(sentences)
            
            
            
            
if __name__ == '__main__':
    m = main()
    m.option_parser()
    m.main()
