import re
import datetime
DELTA_ZERO = datetime.timedelta(days = 0)

def format_delta(delta):
  delta = str(delta).strip('[0:]')
  if delta and not re.search(':', delta): delta = " ".join([delta, 'ms'])
  return delta

class Delta:
  def __init__(self, ms=0):
    self._value = datetime.timedelta(milliseconds = ms)

  def __repr__(self):
    if self.value > DELTA_ZERO:
      return format_delta(self._value)
    else:
      return "-%s" % format_delta(DELTA_ZERO - self.value)

  def advance(self, ms):
    self._value = self._value - datetime.timedelta(milliseconds = ms)

  value = property(lambda self: self._value)
  less_than_zero = property(lambda self: self.value < DELTA_ZERO)
