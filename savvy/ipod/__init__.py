# This class was essentially deprectated as soon as it was created. The
# objective is to have all data sources feed a CouchDB database that will
# select the most up-to-date info for each track. However, we're still
# cleaning up the iTunes database, so we're not ready to comingle data.
#
# Instead, we're reading from the ipod directly but treating it as an object
# so that we can later swap the CouchDB interface in seamlessly.

import gpod
import datetime

class Database:
  def __init__(self, path):
    self.db = gpod.Database(path, None)

  def __iter__(self):
    self.n = 0
    return self

  def next(self):
    if self.n < len(self.db):
      result = self.db[self.n]
      self.n = self.n + 1
      return Track(result)
    else:
      raise StopIteration

# Abstract away access to track information. This will allow us to conform
# ipod, itunes and rss feeds that use different names for the same fields.
class Track:
  def __init__(self, track):
    self.track = track

  def __repr__(self):
    my_class = self.__class__
    return "<%s.%s: %s [%s]>" % (my_class.__module__, my_class.__name__,
                            self.get('title'), self.get('album'))

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
