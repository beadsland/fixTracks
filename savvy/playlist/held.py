import savvy.playlist
import savvy.common

# By default, sort and return everything
def sort_held(held, onzero = False):
  choices = [(held[key].timeout, key, held[key]) for key in held]
  if onzero:
    choices = [(tout, k, s) for (tout, k, s) in choices if tout.less_than_zero]
  return sorted(choices, key=lambda held: held[0].value)

class Held:
  def __init__(self, iter=None, timeout=0):
    if isinstance(timeout, savvy.common.Delta):
      self.timeout = timeout
    else:
      self.timeout = savvy.common.Delta(timeout)
    self.iter = iter
    self.queue = []

  def __iter__(self):
    return self

  def next(self):
    if self.iter:
      return next(self.iter)
    elif len(self.queue):
      return self.queue.pop(0)
    else:
      raise StopIteration

  def __repr__(self):
    if self.iter:
      return repr(self.iter)
    else:
      return "<%s: %s>" % (self.__class__.__name__,
                           savvy.playlist.ReprArray(self.queue))

  def append(self, track):
    if self.iter:
      raise UserWarning("can't append to Held wrapping an iterable")
    self.queue.append(track)

  def defer(self, ms):
    self.timeout = savvy.common.Delta(ms)

  def advance(self, ms):
    self.timeout.advance(ms)
