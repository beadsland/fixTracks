# Copyright 2020 Beads Land-Trujillo

import collections
import itertools

class LazyDict(collections.MutableMapping):
  def __init__(self, source, keyfunc, dict=None):
    self._source = iter(source)
    if not callable(keyfunc):
      raise LookupError(': '.join(['bad keyfunc', keyfunc]))
    self._keyfunc = keyfunc
    self._dict = dict if dict else {}

  def __len__(self):
    if self._source:
      raise AttributeError("length undetermined")
    else:
      return len(self._dict)

  def __iter__(self):
    def tail():
      while True: yield self._next_key()
    return itertools.chain(self._dict, tail())

  def _next_key(self):
    item = next(self._source)
    key = self._keyfunc(item)

    if key in self._dict:
      raise LookupError(': '.join(["non-unique key", key]))
    self._dict[key] = item

    return key

  def __getitem__(self, key):
    if isinstance(key, slice):
      raise NotImplementedError(': '.join(["unsliceable",
                                           self.__class__.__name__]))
    if key in self._dict: return self._dict[key]
    if not self._source: raise KeyError(key)

    while True:
      try:
        if self._next_key() == key: return self._dict[key]
      except StopIteration:
        self._source = None
        raise KeyError(key)

  def __setitem__(self, key, value):
    self._dict[key] = value

  def __delitem__(self, key):
    self.__getitem__(key)
    del(self._dict[key])
