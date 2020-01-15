# Copyright 2020 Beads Land-Trujillo

import re
import datetime

DELTA_ZERO = datetime.timedelta(days = 0)
DELTA_MIN1 = datetime.timedelta(minutes = 1)
DELTA_SEC1 = datetime.timedelta(seconds = 1)

class ReprArray:
  def __init__(self, arr, max=3):
    if len(arr) > max:
      str = "+:%d" % (len(arr) - max)
      arr = arr[:max]
      arr.append(Literal(str))
    self._arr = arr

  def __repr__(self):
    return repr(self._arr)

class Literal:
  def __init__(self, str): self._str = str
  def __repr__(self): return self._str

class Delta:
  def __init__(self, ms=0):
    if type(ms) is datetime.timedelta:
      self._value = ms
    else:
      self._value = datetime.timedelta(milliseconds = ms)

  def __repr__(self):
    if self._value < DELTA_ZERO:
      return "-%s" % self._format(DELTA_ZERO - self._value)
    else:
      return self._format(self._value)

  def _format(self, delta):
    if delta < DELTA_SEC1: return "%f ms" % (delta.microseconds / 1000)
    if delta < DELTA_MIN1: return "%d s" % delta.seconds
    return re.sub(r'\.[0-9]+$', '', str(delta).lstrip('[0:]'))

  def advance(self, ms):
    self._value = self._value - datetime.timedelta(milliseconds = ms)

  value = property(lambda self: self._value)
  less_than_zero = property(lambda self: self._value < DELTA_ZERO)
