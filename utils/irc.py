from libs.pythonbot.bot import Bot
from libs.pythonbot.settings import settings
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.internet import defer

from engines.codecs.relex import relex
#from analysis.analysis import relex_analysis

class Godel(Bot):
    def on_pubMessage(self, user, channel, message):
        if channel and message:
            r = relex.relex()
            sentence = r.process(message)
            parsed = r.parse_output(sentence)
            ## then analyze
            #r = relex_analysis()
            #r.analyze([(message, parsed)])
        
class botFactory(protocol.ClientFactory):
    ## a factory for our bot
    protocol = Godel
        
    def __init__(self, channel, password=None):
        self.settings = settings()
        self.channel = channel
        self.password = password
        self.nickname = self.settings.Get("protected.bot_name")
        
    def clientConnectionLost(self, connector, reason):
        """ If we get disconnected, reconnect to server. """
        connector.connect()
        
    def clientConnectionFailed(self, connector, reason):
        print "Connection failed:", reason
        reactor.stop()

def irc():
    s = settings()
    NETWORK = s.Get('protected.irc_network')
    CHANNEL = s.Get('protected.irc_channel')
    f = botFactory(CHANNEL)
    
    reactor.connectTCP(NETWORK, 6667, f)
    reactor.run()
        
    
    
