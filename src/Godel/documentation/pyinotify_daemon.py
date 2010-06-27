from pyinotify import *
from subprocess import PIPE, Popen, call
from optparse import OptionParser
import time
import sys


class ProcessFile(ProcessEvent):
    def my_init(self, options=None):
        self.firefox   = options.post_firefox
        self.log       = options.doc_daemon_log
        self.last_call = 0

    def process_IN_MODIFY(self, event):
        # We have explicitely registered for this kind of event.
        filename = event.name.split('.')
        file_ext = filename[-1]
        
        if file_ext == 'rst' or file_ext == 'py': 
            print 'File modified "%s" ' % (event.name),
            
            cmd = 'sphinx-build -b html . build'
            print 'sphinx return value: ',
            retVal = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE)
            retVal.wait()


            if retVal.returncode != 0:
                print retVal.communicate()
            else:
                print retVal.returncode
            
            if self.firefox and (time.time() - self.last_call > 30):
                FFcmd = 'firefox build/index.html'
                call(FFcmd, shell=True)

            if self.log:
                f_handle = file('notify.log', 'a')
                f_handle.write(repr(event) + '\n')
                f_handle.flush()
                f_handle.close()

            self.last_call = time.time()


    def process_default(self, event):
        print 'default: ', event.maskname



class main:
    def __init__(self):
        self.parser = OptionParser()
        
        self.parser.add_option("--post-firefox", action="store_true",  dest="doc_firefox", default=False)
        self.parser.add_option("--with-log", action="store_true",  dest="log", default=False)
        self.options, self.args = self.parser.parse_args()

    def main(self):
        print '==> monitoring %s (type ^c to exit)' % os.getcwd()
        handler = ProcessFile(options=self.options)
        wm = WatchManager()
        notifier = ThreadedNotifier(wm, default_proc_fun=handler)
        ## rec is recursive and we want that set
        wm.add_watch('.', IN_MODIFY, rec=True)
        wm.add_watch('../', IN_MODIFY, rec=True)
        notifier.loop()

if __name__ == "__main__":
    main_c = main()
    main_c.main()

