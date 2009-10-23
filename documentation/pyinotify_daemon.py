from pyinotify import *
from subprocess import PIPE, Popen, call
from optparse import OptionParser

import sys


class ProcessFile(ProcessEvent):
    def my_init(self, firefox=False):
        self.firefox = firefox

    def process_IN_MODIFY(self, event):
        # We have explicitely registered for this kind of event.
        filename = event.name.split('.')
        file_ext = filename[-1]
        if file_ext == 'rst':
            print 'File modified "%s" ' % (event.name),

            cmd = 'sphinx-build -b html . build'
            print 'sphinx return value: ',
            retVal = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE)
            retVal.wait()

            if retVal.returncode != 0:
                print retVal.communicate()
            else:
                print retVal.returncode
            
            if self.firefox:
                FFcmd = 'firefox build/index.html'
                call(FFcmd, shell=True)
            
    def process_default(self, event):
        print 'default: ', event.maskname



class main:
    def __init__(self):
        self.parser = OptionParser()
        self.wm = WatchManager()
        self.parser.add_option("--firefox", action="store_true",  dest="firefox", default=False)

        self.options, self.args = self.parser.parse_args()

    def main(self):
        print '==> monitoring %s (type ^c to exit)' % os.getcwd()
        handler = ProcessFile(firefox=self.options.firefox)
        notifier = ThreadedNotifier(self.wm, default_proc_fun=handler)
        ## rec is recursive and we want that set
        self.wm.add_watch('.', IN_MODIFY, rec=True)
        notifier.loop()

if __name__ == "__main__":
    main_c = main()
    main_c.main()

