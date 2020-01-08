import savvy.playlist

# By default, sort and return everything
def sort_held(held, onzero = False):
  choices = [(held[key].timeout, key, held[key]) for key in held]
  if onzero:
    choices = [(tout, k, s) for (tout, k, s) in choices if tout.less_than_zero]
  return sorted(choices, key=lambda held: held[0].value)


class Held:
  def __init__(self, iter=None, timeout=0):
    if isinstance(timeout, Delta):
      self.timeout = timeout
    else:
      self.timeout = Delta(timeout)
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
      return "<%s: %s>" % (self.__class__.__name__, repr(self.iter))
    else:
      return "<%s: %s>" % (self.__class__.__name__,
                           savvy.playlist.repr_array(self.queue))

  def append(self, track):
    if self.iter:
      raise UserWarning("can't append to Held wrapping an iterable")
    self.queue.append(track)

  def defer(self, ms):
    self.timeout = Delta(ms)

  def advance(self, ms):
    self.timeout.advance(ms)

import datetime
DELTA_ZERO = datetime.timedelta(days = 0)

class Delta:
  def __init__(self, ms=0):
    self._value = datetime.timedelta(milliseconds = ms)

  def __repr__(self):
    if self.value > DELTA_ZERO:
      return str(self._value).strip('[0:]')
    else:
      return "-%s" % str(DELTA_ZERO - self.value).strip('[0:]')

  def advance(self, ms):
    self._value = self._value - datetime.timedelta(milliseconds = ms)

  value = property(lambda self: self._value)
  less_than_zero = property(lambda self: self.value < DELTA_ZERO)
