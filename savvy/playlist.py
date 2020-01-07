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
    my_class = self.__class__
    return "<%s.%s: %s>" % (my_class.__module__, my_class.__name__, self.stagger)

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
    my_class = self.__class__
    return "<%s.%s: %s + %s>" % (my_class.__module__, my_class.__name__,
                                 self.sort_held(), self.feed)

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
    choices = [(self.held[key].timeout, key) for key in self.held]
    if onzero:
      choices = [(t, k) for (t, k) in choices if t <= 0]
    return sorted(choices, key=lambda held: held[0])

class Held:
  def __init__(self, iter = None):
    self.timeout = 0
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

  def append(self, track):
    if self.iter:
      raise UserWarning("can't append to Held wrapping an iterable")
    self.queue.append(track)

  def defer(self, ms):
    self.timeout = ms

  def advance(self, ms):
    self.timeout = self.timeout - ms
