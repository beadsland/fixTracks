import savvy.playlist
import savvy.playlist.held

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
    heldstr = savvy.playlist.repr_array(savvy.playlist.held.sort_held(self.held),
                                        self.feed)
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
      self.held[key] = savvy.playlist.held.Held()
    self.held[key].append(track)

  # Release furthest advanced track with deferral < 0, until we can't.
  def next_free(self, onzero = True):
    choices = savvy.playlist.held.sort_held(self.held, onzero)

    if len(choices):
      key = choices[0][1]
      return self._emit(key)
    else:
      return self.next_uniq()

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
