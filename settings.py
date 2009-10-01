from libs.configobj import ConfigObj

SETTING_FILE = "settings.cfg"

class settings:
    def __init__(self):
        self.settings = ConfigObj(SETTING_FILE)
        
    def settings(self):
        return self.settings
     
    def Get(self, setting):
        """expecting input like 'section.setting'"""
        try:
            return reduce(dict.get, setting.split('.'), self.settings)
        except:
            return False
