import scheme
def a():
    pass

s = scheme.scheme()
s.set_callback('abc',a)
s.set_callback('abc2',a)
print s.run_file('test.scm')
print s.callbacks
