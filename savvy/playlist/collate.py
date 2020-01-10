# Copyright 2020 Beads Land-Trujillo

import savvy.playlist.stagger
import savvy.playlist.held

import re

class Collate:
  def __init__(self, piles):
    holds = {}
    defer = 0

    while len(piles):
      (name, share, iter) = piles.pop(0)

      defer = defer + 1
      id = "%s %d" % (name, share)
      holds[id] = savvy.playlist.held.Held(iter)
      holds[id].defer(defer)

      share = share - 1
      if share:
        piles.append((name, share, iter))

    self.stagger = savvy.playlist.stagger.Stagger(len(holds), None, None, holds)

  def __iter__(self):
    return self

  def next(self):
    return next(self.stagger)

  def __repr__(self):
    patt = re.compile("^<%s: (.*)>$" % self.stagger.__class__.__name__)
    m = re.match(patt, repr(self.stagger))
    return "<%s: %s>" % (self.__class__.__name__, m.groups()[0])
