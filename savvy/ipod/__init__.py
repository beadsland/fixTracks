# This class was essentially deprectated as soon as it was created. The
# objective is to have all data sources feed a CouchDB database that will
# select the most up-to-date info for each track. However, we're still
# cleaning up the iTunes database, so we're not ready to comingle data.
#
# Instead, we're reading from the ipod directly but treating it as an object
# so that we can later swap the CouchDB interface in seamlessly.

import gpod

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
      return result
    else:
      raise StopIteration
