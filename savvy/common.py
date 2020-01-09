import re
import datetime
DELTA_ZERO = datetime.timedelta(days = 0)

class ReprArray:
  def __init__(self, arr, max=3):
    if len(arr) > max:
      str = "+:%d" % (len(arr) - max)
      arr = arr[:max]
      arr.append(Literal(str))
    self.arr = arr

  def __repr__(self):
    return repr(self.arr)

class Literal:
  def __init__(self, str): self.str = str
  def __repr__(self): return self.str

class Delta:
  def __init__(self, ms=0):
    self._value = datetime.timedelta(milliseconds = ms)

  def __repr__(self):
    return self._format(self.value < DELTA_ZERO)

  def _format(self, minus=False):
    delta = str(self.value).strip('[0:]')
    if delta and not re.search(':', delta): delta = " ".join([delta, 'ms'])
    if delta and minus: delta = "-%s" % delta
    return delta

  def advance(self, ms):
    self._value = self._value - datetime.timedelta(milliseconds = ms)

  value = property(lambda self: self._value)
  less_than_zero = property(lambda self: self.value < DELTA_ZERO)
