import sys

class TailRecurseException:
  def __init__(self, args, kwargs):
    self.args = args
    self.kwargs = kwargs

def trampoline(function):
  """
  This function decorates a function with tail call
  optimization. It does this by throwing an exception
  if it is it's own grandparent, and catching such
  exceptions to fake the tail call optimization.
  
  This function fails if the decorated
  function recurses in a non-tail context.
  """
  def func(*args, **kwargs):
    frame = sys._getframe()
    if frame.f_back and frame.f_back.f_back \
        and frame.f_back.f_back.f_code == frame.f_code:
      raise TailRecurseException(args, kwargs)
    else:
      while 1:
        try:
          return function(*args, **kwargs)
        except TailRecurseException, e:
          args = e.args
          kwargs = e.kwargs
          
  func.__doc__ = function.__doc__
  return func


