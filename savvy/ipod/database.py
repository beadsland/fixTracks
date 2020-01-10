# Copyright 2020 Beads Land-Trujillo

import savvy.ipod.track
import savvy.ipod.playlist

import os
import usb.core
import tempfile
import pathlib
import datetime

IPOD_CTRL = "iPod_Control"
IPOD_BORN = datetime.datetime(2001, 10, 23, 0, 0, 0)

class Database:
  def __init__(self, path):
    import gpod
    self._db = gpod.Database(path, None)

  def normalize_bad_clocktime(self):
    now = datetime.datetime.now()
    tracks = [savvy.ipod.track.Track(t) for t in self._db]
    bad = [t for t in tracks if t.played_date and t.played_date < IPOD_BORN]

    if bad:
      bad = sorted(bad, key = lambda t: t.played_date)
      maxbad = max(t.played_date for t in bad)

      floor = datetime.datetime(1999, 12, 31, 0, 0, 0)
      pocket = datetime.timedelta(hours = 12)
      fix = maxbad - floor + pocket

      for t in bad:
        fixtime = now - fix + (t.played_date - floor)
        print "* Adjusting %s to %s for %s" % (t.played_date, fixtime, t)
        t.as_libgpod['time_played'] = fixtime

  as_libgpod = property(lambda self: self._db)

  def __iter__(self):
    self._n = 0
    return self

  def next(self):
    if self._n < len(self._db):
      result = self._db[self._n]
      self._n = self._n + 1
      return savvy.ipod.track.Track(result)
    else:
      raise StopIteration

  def __del__(self):
    print "Committing changes to iPod database. Please wait..."
    self.close()
    print "Done"

  def close(self):
    self._db.copy_delayed_files()
    self._db.close()

    print "Attempting to eject iPod..."
    sema = os.path.join(tempfile.gettempdir(), "do_ipodEjectDaemon_semaphore")
    pathlib.Path(sema).touch()

  def playlists(self):
    return {p.name: savvy.ipod.playlist.Playlist(p)
            for p in self._db.get_playlists()}

  def get_playlist(self, name):
    return self.playlists()[name]

  def add_playlist(self, name):
    plist = self._db.new_Playlist(title=name) # weird case in case weird
    return savvy.ipod.playlist.Playlist(plist)

  def wipe_playlist(self, name):
    if name not in self.playlists():
      self.add_playlist(name)

    plist = self.get_playlist(name).as_libgpod

    for track in reversed(plist):
      plist.remove(track)

    return savvy.ipod.playlist.Playlist(plist)
