# Copyright 2020 Beads Land-Trujillo

import datetime

IPOD_NULL = datetime.datetime(1970, 1, 1, 14, 0, 0)

class Track:
  def __init__(self, track):
    self._track = track

  def __repr__(self):
    my_class = self.__class__
    return "<%s %s: %s [%s]>" % ("iPod", my_class.__name__,
                                 self.get('title'), self.get('album'))

  as_libgpod = property(lambda self: self._track)

  def get(self, key):
    return self._track[key]

  def get_date(self, key, min=False):
    try:
      if self.get(key) <= IPOD_NULL:
        return None
      else:
        return self.get(key)
    except:
      if min:
        return datetime.datetime.min
      else:
        return None

  release_date = property(lambda self: self.get_date('time_released'))
  release_date_sortable = property(lambda s: s.get_date('time_released', True))
  played_date = property(lambda self: self.get_date('time_played'))

  bookmark_time = property(lambda self: self.get('bookmark_time'))
  tracklen_time = property(lambda self: self.get('tracklen'))

  playcount = property(lambda self: self.get('playcount'))
  playtime = property(lambda self: self.tracklen_time - self.bookmark_time)

  # need a method that checks for podcast alias album names
  album_title = property(lambda self: self.get('album'))
  podcast_title = property(lambda self: self.album_title)
