# Copyright 2020 Beads Land-Trujillo

import savvy.ipod.track
import savvy.ipod.playlist

import gpod

import os
import usb.core
import tempfile
import pathlib
import datetime

IPOD_CTRL = "iPod_Control"
IPOD_BORN = datetime.datetime(2001, 10, 23, 0, 0, 0)

class Database:
  def __init__(self, path):
    idb_path = os.path.join(path, IPOD_CTRL, 'iTunes', 'iTunesDB')
    mdate = datetime.datetime.fromtimestamp(os.path.getmtime(idb_path))
    if mdate < IPOD_BORN: mdate = datetime.datetime.now()

    self._mdate = mdate
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
  modified_date = property(lambda self: self._mdate)

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

  tracks = property(lambda self: self._all_tracks())
  playlists = property(lambda self: self._user_playlists())

  def _all_tracks(self):
    tracks = [savvy.ipod.track.Track(t) for t in self._db]
    return {t.persist_id: t for t in tracks}

  def _all_playlists(self):
    return {p.name: savvy.ipod.playlist.Playlist(p) for p
                                                    in self._db.get_playlists()}

  def _user_playlists(self):
    all = self._all_playlists()
    return {k: all[k] for k in all if not (all[k].is_master_music
                                           or all[k].is_master_podcast)}

  def get_playlist(self, name):
    return self.playlists[name]

  def add_playlist(self, name):
    if name in self.playlists:
      raise ValueError("playlist already exists")
    else:
      plist = self._db.new_Playlist(title=name) # weird case in case weird
      return savvy.ipod.playlist.Playlist(plist)

  def drop_playlist(self, name):
    plist = self.playlists[name]
    if plist.is_master_music or plist.is_master_podcast:
      raise TypeError("system playlist cannot be removed")
    plist.wipe()
    self._db.remove(plist.as_libgpod)
