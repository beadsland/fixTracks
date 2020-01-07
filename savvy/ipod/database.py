import savvy.ipod.track

import os
import usb.core
import tempfile
import pathlib

IPOD_CTRL = "iPod_Control"

class Database:
  def __init__(self, path):
    import gpod
    self.db = gpod.Database(path, None)
    self.path = path

  as_libgpod = property(lambda self: self.db)

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

    print "Attempting to eject iPod..."
    sema = os.path.join(tempfile.gettempdir(), "do_ipodEjectDaemon_semaphore")
    pathlib.Path(sema).touch()

  def playlists(self):
    return {p.name: p for p in self.db.get_playlists()}

  def get_playlist(self, name):
    return self.playlists()[name]

  def add_playlist(self, name):
    return self.db.new_Playlist(title=name) # weird case in case weird

  def wipe_playlist(self, name):
    if name not in self.playlists():
      self.add_playlist(name)

    plist = self.get_playlist(name)

    for track in reversed(plist):
      plist.remove(track)

    return plist
