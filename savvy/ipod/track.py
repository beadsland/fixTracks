import datetime

# Abstract away access to track information. This will allow us to conform
# ipod, itunes and rss feeds that use different names for the same fields.
class Track:
  def __init__(self, track):
    self.track = track

  def __repr__(self):
    my_class = self.__class__
    return "<%s.%s: %s [%s]>" % (my_class.__module__, my_class.__name__,
                            self.get('title'), self.get('album'))

  def as_libgpod(self):
    return self.track

  def get(self, key):
    return self.track[key]

  def get_date(self, key, min=True):
    try:
      return self.get(key)
    except:
      if min:
        return datetime.datetime.min
      else:
        return None

  release_date = property(lambda self: self.get_date('time_released'))
  playcount = property(lambda self: self.get('playcount'))
  bookmark_time = property(lambda self: self.get('bookmark_time'))
  tracklen_time = property(lambda self: self.get('tracklen'))
  playtime = property(lambda self: self.tracklen_time - self.bookmark_time)

  # need a method that checks for podcast alias album names
  album_title = property(lambda self: self.get('album'))
  podcast_title = property(lambda self: self.album_title)
