# Copyright 2020 Beads Land-Trujillo

import savvy.common
import savvy.playlist.held

def split_zero(fin, tup):
  (belowzero, abovezero) = fin
  (defer, prop, hold) = tup
  if defer.less_than_zero:
    belowzero.append(tup)
  else:
    abovezero.append(tup)
  return (belowzero, abovezero)

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
        return self._next_uniq()
      else:
        return self._next_free()
    else:
      if len(self.held):
        return self._next_free(False)
      else:
        raise StopIteration

  def __repr__(self):
    arr = savvy.playlist.held.sort_held(self.held)

    (belowzero, abovezero) = reduce(split_zero, arr, ([], []))

    forelen = min(3, len(belowzero))
    backlen = min(3, max(3, len(abovezero) - forelen))
    if self.feed is not None:
      if forelen > 0: forelen -=1
      else: backlen -= 1

    if len(belowzero):
      belowzero = savvy.common.ReprArray(belowzero, forelen)
    if len(abovezero):
      abovezero = savvy.common.ReprArray(abovezero, max(0, backlen))

    arr = [belowzero, abovezero]
    if self.feed: arr.insert(1, self.feed)

    arr = [repr(item) for item in arr if item]

    return "<%s: %s>" % (self.__class__.__name__, ' + '.join(arr))

  # We want at least denom sources held before we release any.
  def _next_uniq(self):
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
      self.held[key] = savvy.playlist.held.Held()
    self.held[key].append(track)

  # Release furthest advanced track with deferral < 0, until we can't.
  def _next_free(self, onzero = True):
    choices = savvy.playlist.held.sort_held(self.held, onzero)

    if len(choices):
      key = choices[0][1]
      return self._emit(key)
    else:
      return self._next_uniq()

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
