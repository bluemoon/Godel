from settings import settings
import cPickle
import hashlib
import inspect
import os


## get the setting for the data directory
s = settings()
DATA_FOLDER = s.Get('general.data_directory')
GLOBAL_MAX = s.Get('memoize.max_size')
FUNC_MAX = s.Get('memoize.per_function')

cachedir = DATA_FOLDER + "pickles/"
## if no directory, make it
if not os.path.exists(cachedir): os.mkdir(cachedir)

def file_hash(file):
    f_handle = open(file)
    sha1 = hashlib.sha1()
    sha1.update(f_handle.read())
    f_hash = sha1.hexdigest()
    f_handle.close()
    
    return f_hash


def folder_size(folder, starts_with=None):
    ## determine size of a given folder in MBytes
    ## true mb's 1024 * 1024
    folder_size = 0
    for (path, dirs, files) in os.walk(folder):
        for file in files:
            if starts_with:
                if not file.startswith(starts_with):
                    continue
            
            filename = os.path.join(path, file)
            folder_size += os.path.getsize(filename)
       
    #print "Folder = %0.1f MB" % (folder_size/(1024*1024.0))
    return (folder_size/(1024.0*1024.0))

        
def run_anyway(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args)
        except:
            return func(*args)

def persistent_memoize(func, limit=None):
    inspect_stack = inspect.stack()
    caller_module = inspect_stack[1][1]
    dict_file = os.path.join(cachedir, "global-cache.pickle")
    
    if os.path.exists(dict_file):
        try:
            f_handle = open(dict_file)
            global_dict = cPickle.load(f_handle)
            f_handle.close()
        except KeyboardInterrupt:
            try:
                f_handle.close()
            except:
                pass
    else:
        global_dict = {}
    
    if isinstance(func, int):
        def memoize_wrapper(f):
            return memoize(f, func)

        return memoize_wrapper
    
    def memoize_wrapper(*args, **kwargs):
        #f_hash = file_hash(caller_module)
        
        ## per function folders to keep it clean
        cache_dir = cachedir + '%s_func/' % (func.func_name)
        if not os.path.exists(cache_dir): os.mkdir(cache_dir)
        ## get the cache sizes
        func_size = folder_size(cache_dir)
        global_size = folder_size(cachedir)
        ## dump the string with cpickle and check the hash
        key = cPickle.dumps((args, kwargs))
        true_key = hashlib.sha224(key).hexdigest()
        ## store per hash vs one file because of file load time
        file = os.path.join(cache_dir, "%s-%s.pickle" % (func.func_name, true_key))

        if global_dict.has_key(true_key):
            global_dict[true_key]['call_count'] += 1
        else:
            global_dict[true_key] = {}
            global_dict[true_key]['call_count'] = 0
            global_dict[true_key]['func_name']  = func.func_name
            #global_dict[true_key]['file_hash']  = f_hash
        try:
            f_handle = open(dict_file, 'w')
            cPickle.dump(global_dict, f_handle)
            f_handle.close()
        except KeyboardInterrupt:
            f_handle = open(dict_file, 'w')
            cPickle.dump(global_dict, f_handle)
            f_handle.close()
            
        
        if os.path.exists(file):
            f_handle = open(file)
            c = cPickle.load(f_handle)
            f_handle.close()
        else:
            c = {}
        
        if c.has_key(key):
            return c[key]
        else:
            if func_size > FUNC_MAX or global_size > GLOBAL_MAX:
                return func(*args, **kwargs)
            
            c[key] = func(*args, **kwargs)
            ## pickle to disk
            f = open(file, 'w')
            cPickle.dump(c, f)
            f.close()
            ## then return
            return c[key]
        
    return memoize_wrapper

def memoize(function, limit=None):
    if isinstance(function, int):
        def memoize_wrapper(f):
            return memoize(f, function)

        return memoize_wrapper

    dict = {}
    list = []
    def memoize_wrapper(*args, **kwargs):
        key = cPickle.dumps((args, kwargs))
        try:
            list.append(list.pop(list.index(key)))
        except ValueError:
            dict[key] = function(*args, **kwargs)
            list.append(key)
            if limit is not None and len(list) > limit:
                del dict[list.pop(0)]

        return dict[key]

    memoize_wrapper._memoize_dict = dict
    memoize_wrapper._memoize_list = list
    memoize_wrapper._memoize_limit = limit
    memoize_wrapper._memoize_origfunc = function
    memoize_wrapper.func_name = function.func_name
    return memoize_wrapper
