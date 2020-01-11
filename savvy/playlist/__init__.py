# Copyright 2020 Beads Land-Trujillo

class Playlist:
  def __init__(self, feed, cap=24, hcap=None):
    if not hcap: hcap = cap /2

    history_filter = (lambda t: t.playcount or t.skipped_date, cap)
    roster_filter = (lambda t: not t.playcount, hcap)
    self._bifurcate = Bifurcate(feed, history_filter, roster_filter)
    self._needle = self._find_needle()

  def __iter__(self):
    self._iter = itertools.chain([self._needle], self._bifurcate.history)

  def next(self):
    return next(self._iter)

  history = property(lambda self: self._bifurcate.history)
  needle = property(lambda self: self._needle)
  roster = property(lambda self: self._bifurcate.roster)

class Bifurcate:
  def __init__(self, feed, history_filter, roster_filter):
    self._feed = feed
    self._hfilter = history_filter
    self._rfilter = roster_filter

# Brainstorming...
  # history and roster are iterable ?queues? built from filters of feed

  # roster blocks on a call to parent's filter_function
  # roster returns until cap reached

  # needle seeks last skipped_date, absent that first bookmark in roster

  # history blocks until cap entries are received and then reverse sorted
  # history returns until hcap reached
