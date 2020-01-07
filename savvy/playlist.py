def repr_array(arr, plus=None):
  if not len(arr):
    out = "[]"
  elif len(arr) < 4:
    out = str(arr[:3])
  else:
    out = "%s, ... of %d]" % (str(arr[:3]).rstrip("]"), len(arr))

  if plus:
    return "%s + %s" % (out, plus)
  else:
    return out

class Collate:
  def __init__(self, piles):
    holds = {}
    defer = 0

    while len(piles):
      (name, share, iter) = piles.pop(0)

      defer = defer + 1
      id = "%s %d" % (name, share)
      holds[id] = Held(iter)
      holds[id].defer(defer)

      share = share - 1
      if share:
        piles.append((name, share, iter))

    self.stagger = Stagger(len(holds), None, None, holds)

  def __iter__(self):
    return self

  def next(self):
    return next(self.stagger)

  def __repr__(self):
    return "<%s: %s>" % (self.__class__.__name__, repr(self.stagger))

class Stagger:
  def __init__(self, denom, prop, feed, hold=None):
    self.denom = denom
    self.prop = prop
    self.feed = feed
    self.held = hold
    if self.held is None: self.held = {}

  def __iter__(self):
    return self

  def next(self):
    if self.feed:
      if len(self.held) < self.denom:
        return self.next_uniq()
      else:
        return self.next_free()
    else:
      if len(self.held):
        return self.next_free(False)
      else:
        raise StopIteration

  def __repr__(self):
    heldstr = repr_array(self.sort_held(), self.feed)
    return "<%s: %s>" % (self.__class__.__name__, heldstr)

  # We want at least denom sources held before we release any.
  def next_uniq(self):
    try:
      track = next(self.feed)
    except:
      self.feed = None
      return self.next()

    for h in self.held:
      self.held[h].advance(1)

    self._defer(track)
    return self.next()

  def _defer(self, track):
    key = getattr(track, self.prop)
    if key not in self.held:
      self.held[key] = Held()
    self.held[key].append(track)

  # Release furthest advanced track with deferral < 0, until we can't.
  def next_free(self, onzero = True):
    choices = self.sort_held(onzero)

    if len(choices):
      key = choices[0][1]
      return self._emit(key)
    else:
      return self.next()

  def _emit(self, key):
    try:
      track = next(self.held[key])
    except StopIteration:
      del(self.held[key])
      return self.next()

    for h in self.held:
      if h != key:
        self.held[h].advance(track.playtime)
    self.held[key].defer(track.playtime)
    return track

  # By default, sort and return everything
  def sort_held(self, onzero = False):
    choices = [(self.held[key].timeout, key, self.held[key]) for key in self.held]
    if onzero:
      choices = [(tout, k, s) for (tout, k, s) in choices if tout <= 0]
    return sorted(choices, key=lambda held: held[0].value)

class Held:
  def __init__(self, iter=None, timeout=0):
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
      return "<%s: %s>" % (self.__class__.__name__, repr_array(self.queue))

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
    if type(ms) is self.__class__:
      ms = ms.value
    self._value = datetime.timedelta(milliseconds = ms)

  def __repr__(self):
    if self.value > DELTA_ZERO:
      return str(self._value).strip('[0:]')
    else:
      return "-%s" % str(DELTA_ZERO - self.value).strip('[0:]')

  def advance(self, ms):
    self._value = self._value - datetime.timedelta(milliseconds = ms)

  value = property(lambda self: self._value)
