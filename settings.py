from libs.configobj.configobj import ConfigObj
import os

SETTING_FILE = os.path.dirname(__file__) + "/settings.cfg"

class settings:
    def __init__(self):
        self.settings = ConfigObj(SETTING_FILE, unrepr=True)
        
    def Get(self, setting):
        """expecting input like 'section.setting'"""
        try:
            return reduce(dict.get, setting.split('.'), self.settings)
        except:
            return False
