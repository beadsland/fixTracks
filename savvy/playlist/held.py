# Copyright 2020 Beads Land-Trujillo

import savvy.common

class AppendToIteratorError(Exception): pass

class Held:
  def __init__(self, iter=None, timeout=0):
    if isinstance(timeout, savvy.common.Delta):
      self._timeout = timeout
    else:
      self._timeout = savvy.common.Delta(timeout)
    self._iter = iter
    self._queue = []

  def __iter__(self):
    return self

  def next(self):
    if self._iter:
      return next(self._iter)
    elif len(self._queue):
      return self._queue.pop(0)
    else:
      raise StopIteration

  def __repr__(self):
    if self._iter:
      return repr(self._iter)
    elif not self._queue:
      return "None"
    else:
      return "<%s: %s>" % (self.__class__.__name__,
                           savvy.common.ReprArray(self._queue))

  timeout = property(lambda self: self._timeout)

  def append(self, track):
    if self._iter:
      raise AppendToIteratorError()
    self._queue.append(track)

  def defer(self, ms):
    self._timeout = savvy.common.Delta(ms)

  def advance(self, ms):
    self._timeout.advance(ms)
