# Copyright 2020 Beads Land-Trujillo

import savvy.ipod.track

class Playlist:
  def __init__(self, plist):
    self._plist = plist

  def __repr__(self):
    my_class = self.__class__
    return "<%s %s: %s [%d tracks]>" % ("iPod", my_class.__name__,
                                        self.get('name'), len(self._plist))

  as_libgpod = property(lambda self: self._plist)
  is_master_music = property(lambda self: self._plist.get_master())
  is_master_podcast = property(lambda self: self._plist.get_podcast())

  def __iter__(self):
    self._iter = iter(self._plist)
    return self

  def next(self):
    return savvy.ipod.track.Track(next(self._iter))

  def __len__(self):
    return len(self._plist)

  def add(self, track, pos=-1):
    self._plist.add(track.as_libgpod, pos)

  def wipe(self):
    for track in reversed(self._plist):
      self._plist.remove(track)
