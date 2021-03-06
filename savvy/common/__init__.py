# Copyright 2020 Beads Land-Trujillo

import re
import datetime
import sys
import itertools

DELTA_ZERO = datetime.timedelta(days = 0)
DELTA_MIN1 = datetime.timedelta(minutes = 1)
DELTA_SEC1 = datetime.timedelta(seconds = 1)

FLYWHEEL = iter(itertools.cycle("/-\\|"))
def flywheel(): return next(FLYWHEEL)
def spin_flywheel(): write(flywheel(), False)

def write(str, clear=True):
  sys.stdout.write(str)
  if clear: sys.stdout.write("\033[K")
  sys.stdout.write("\r")
  sys.stdout.flush()

class ReprArray:
  def __init__(self, arr, cap=3):
    if len(arr) and len(arr) > cap:
      str = "+:%d" % (len(arr) - max(cap, 0))
      arr = arr[:cap]
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
    if delta < DELTA_SEC1: return "%s ms" % str(delta.microseconds / 1000)
    if delta < DELTA_MIN1: return "%d s" % delta.seconds
    return re.sub(r'\.[0-9]+$', '', str(delta).lstrip('[0:]'))

  def advance(self, ms):
    self._value = self._value - datetime.timedelta(milliseconds = ms)

  value = property(lambda self: self._value)
  less_than_zero = property(lambda self: self._value < DELTA_ZERO)
