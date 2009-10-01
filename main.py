from optparse import OptionParser
from settings import DATA_FOLDER

class main:
    def option_parser(self):
        self.parser = OptionParser()
        self.parser.add_option("--rule-engine", dest="engine")
        self.parser.add_option("--source", dest="source")
        (self.options, self.args) = self.parser.parse_args()

    def main(self):
        self.source = None
        if self.options.source == 'irc-logs':
            from input.irc_log import irc_logParser
            
            logParser = irc_logParser()
            self.source = logParser.loadLogs(DATA_FOLDER + 'logs/2009-08-1*', limit=200)

            assert len(self.source) > 0, 'irc source is invalid.'
            
            
if __name__ == '__main__':
    m = main()
    m.option_parser()
    m.main()
