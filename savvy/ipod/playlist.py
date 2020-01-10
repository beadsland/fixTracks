# Copyright 2020 Beads Land-Trujillo

import savvy.ipod.track

class Playlist:
  def __init__(self, plist):
    self.plist = plist

  def __repr__(self):
    my_class = self.__class__
    return "<%s %s: %s [%d tracks]>" % ("iPod", my_class.__name__,
                                        self.get('name'), len(self.plist))

  as_libgpod = property(lambda self: self.plist)

  def __iter__(self):
    self.iter = iter(self.plist)
    return self

  def next(self):
    return savvy.ipod.track.Track(next(self.iter))

  def __len__(self):
    return len(self.plist)

  def add(self, track, pos=-1):
    self.plist.add(track.as_libgpod, pos)
