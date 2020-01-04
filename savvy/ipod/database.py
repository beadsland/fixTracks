import savvy.ipod.track

import os
import usb.core

class Database:
  def __init__(self, path):
    import gpod
    self.db = gpod.Database(path, None)
    self.path = path

  def __iter__(self):
    self.n = 0
    return self

  def next(self):
    if self.n < len(self.db):
      result = self.db[self.n]
      self.n = self.n + 1
      return savvy.ipod.track.Track(result)
    else:
      raise StopIteration

  def __del__(self):
    print "Committing changes to iPod database. Please wait..."
    self.close()
    print "Done"

  def close(self):
    self.db.copy_delayed_files()
    self.db.close()
#    os.system("umount \"%s\"" % self.path)

  def playlists(self):
    return {p.name: p for p in self.db.get_playlists()}

  def add_playlist(self, name):
    return self.db.new_Playlist(title=name) # weird case in case weird
