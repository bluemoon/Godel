from settings import settings

import os
import cPickle

s = settings()
DATA_FOLDER = s.Get('general.data_directory')
cachedir = DATA_FOLDER + "pickles/"

def save_state(state, class_name):
    file = os.path.join(cachedir, "class-%s.pickle" % (class_name))
    f_handle = open(file, 'w')
    cPickle.dump(state, f_handle)
    f_handle.close()

def load_state(class_name):
    file = os.path.join(cachedir, "class-%s.pickle" % (class_name))
    if os.path.exists(file):
        f_handle = open(file, 'r')
        state = cPickle.load(f_handle)
        f_handle.close()
        
        return (True, state)
    
    else:
        return (False, None)
