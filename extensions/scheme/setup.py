from distutils.core import setup, Extension

module1 = Extension('scheme',
                    sources = ['scheme.c'],
                    include_dirs = ['/home/bluemoon/Projects/libscheme-0.5'],
                    libraries = ['scheme'],
                    library_dirs = ['/home/bluemoon/Projects/libscheme-0.5'],
                    )

setup (name = 'scheme',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
