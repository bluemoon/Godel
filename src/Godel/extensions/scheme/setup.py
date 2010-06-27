from distutils.core import setup, Extension

module1 = Extension('scheme',
                    sources = ['scheme.c'],
                    include_dirs = ['/usr/include/', '/usr/include/libguile/'],
                    libraries = ['guile', 'gmp'],
                    library_dirs = ['/usr/lib/'],
                    )

setup (name = 'scheme',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
