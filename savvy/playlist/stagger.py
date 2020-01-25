# Copyright 2020 Beads Land-Trujillo

import savvy.common
import savvy.playlist.held

class Stagger:
  def __init__(self, denom, prop, feed, hold=None):
    if denom < 2:
      raise ValueError(': '.join["not enough zigs to zag", str(denom)])
    self._denom = denom
    self._prop = prop
    self._feed = feed
    self._held = {} if hold is None else hold

  def __iter__(self):
    return self

  def next(self):
    if self._feed:
      if len(self._held) < self._denom:
        return self._next_uniq()
      else:
        return self._next_free()
    else:
      if len(self._held):
        return self._next_free(False)
      else:
        raise StopIteration

  def __repr__(self):
    arr = self._sort_held(self._held)

    (belowzero, abovezero) = reduce(self._split_zero, arr, ([], []))

    forelen = min(3, len(belowzero))
    backlen = min(3-forelen, len(abovezero))
    if self._feed is not None:
      if backlen > 0: backlen -= 1
      elif forelen > 2: forelen -= 1
    if forelen and len(abovezero) and not backlen:
      forelen -= 1; backlen += 1

    print len(belowzero), len(abovezero), forelen, backlen

    if len(belowzero):
      belowzero = savvy.common.ReprArray(belowzero, forelen)
    if len(abovezero):
      abovezero = savvy.common.ReprArray(abovezero, max(0, backlen))

    arr = [belowzero, abovezero]
    if self._feed: arr.insert(1, self._feed)

    arr = [repr(item) for item in arr if item]

    return "<%s: %s>" % (self.__class__.__name__, ' + '.join(arr))

  def _split_zero(_self, fin, tup):
    (belowzero, abovezero) = fin
    (defer, prop, hold) = tup
    if defer.less_than_zero:
      belowzero.append(tup)
    else:
      abovezero.append(tup)
    return (belowzero, abovezero)

  # We want at least denom sources held before we release any.
  def _next_uniq(self):
    try:
      track = next(self._feed)
    except:
      self._feed = None
      return self.next()

    for h in self._held:
      self._held[h].advance(1)

    self._defer(track)
    return self.next()

  def _defer(self, track):
    key = getattr(track, self._prop)
    if key not in self._held:
      self._held[key] = savvy.playlist.held.Held()
    self._held[key].append(track)

  # Release furthest advanced track with deferral < 0, until we can't.
  def _next_free(self, onzero = True):
    choices = self._sort_held(self._held, onzero)

    if len(choices):
      key = choices[0][1]
      return self._emit(key)
    else:
      return self._next_uniq()

  # By default, sort and return everything
  def _sort_held(_self, held, onzero = False):
    choices = [(held[key].timeout, key, held[key]) for key in held]
    if onzero:
      choices = [(tout, k, s) for (tout, k, s) in choices if tout.less_than_zero]
    return sorted(choices, key=lambda held: held[0].value)

  def _emit(self, key):
    try:
      track = next(self._held[key])
    except StopIteration:
      del(self._held[key])
      return self.next()

    for h in self._held:
      if h != key:
        self._held[h].advance(float(track.playtime) / (self._denom - 1))
    self._held[key].defer(track.playtime)
    return track
