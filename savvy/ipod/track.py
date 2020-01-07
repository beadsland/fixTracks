import datetime

IPOD_NULL = datetime.datetime(1969, 12, 31, 19, 0, 0)
MOCK_CEIL = datetime.datetime(2001, 1, 1, 0, 0, 0)

class Track:
  def __init__(self, track):
    self.track = track

  def __repr__(self):
    my_class = self.__class__
    return "<%s.%s: %s [%s]>" % (my_class.__module__, my_class.__name__,
                            self.get('title'), self.get('album'))

  as_libgpod = property(lambda self: self.track)

  def get(self, key):
    return self.track[key]

  def get_date(self, key, min=True):
    try:
      if self.get(key) == IPOD_NULL:
        return None
      else:
        return self.get(key)
    except:
      if min:
        return datetime.datetime.min
      else:
        return None

  def get_mock_played_date(self):
    played = self.played_date
    if played < MOCK_CEIL:
      return datetime.datetime.now() - (MOCK_CEIL - played)
    else:
      return played

  release_date = property(lambda self: self.get_date('time_released'))
  played_date = property(lambda self: self.get_date('time_played'))

  bookmark_time = property(lambda self: self.get('bookmark_time'))
  tracklen_time = property(lambda self: self.get('tracklen'))

  played = property(lambda self: self.playcount
                                 or self.get_date('time_played', False))
  playcount = property(lambda self: self.get('playcount'))
  playtime = property(lambda self: self.tracklen_time - self.bookmark_time)

  # need a method that checks for podcast alias album names
  album_title = property(lambda self: self.get('album'))
  podcast_title = property(lambda self: self.album_title)
