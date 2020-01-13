# Copyright 2020 Beads Land-Trujillo

import gpod
import datetime
import struct
import binascii

IPOD_NULL = datetime.datetime(1970, 1, 1, 14, 0, 0)

class Track:
  def __init__(self, track):
    self._track = track

  def __repr__(self):
    my_class = self.__class__
    return "<%s %s: %s [%s]>" % ("iPod", my_class.__name__,
                                 self.get('title'), self.get('album'))

  as_libgpod = property(lambda self: self._track)

  def dump(self):
    json = {'_persist_id': self.persist_id}
    for key in self._track:
      value = self.get(key)

      if type(value) is datetime.datetime:
        json[key] = value.isoformat()
      elif type(value) in [gpod.gpod._Itdb_iTunesDB, gpod.gpod._Itdb_Artwork]:
        pass
      elif type(value).__name__ == 'SwigPyObject':
        pass
      else:
        json[key] = value.decode('utf-8') if type(value) is str else value
    return json

  def get(self, key, sortdate=False):
    try:
      value = self._track[key]
    except:
      return datetime.datetime.min if sortdate else None

    if type(value) is datetime.datetime:
      return self._sortable_date(value, sortdate)
    else:
      return value

  def _sortable_date(self, value, sortdate=False):
    if value <= IPOD_NULL:
      return datetime.datetime.min if sortdate else None
    else:
      return value

  def _set(self, key, value):
    self._track[key] = value

  def get_persist_id(self):
    return hex(self.get('dbid')).rstrip('L').lstrip('0x').rjust(16, '0').upper()

  def _is_podcast(self):
    return self.get('mediatype') == gpod.ITDB_MEDIATYPE_PODCAST

  persist_id = property(lambda self: self.get_persist_id())
  is_podcast = property(lambda self: self._is_podcast())

  release_date = property(lambda self: self.get('time_released'))
  release_date_sortable = property(lambda self: self.get('time_released', True))
  played_date = property(lambda self: self.get('time_played'))

  bookmark_time = property(lambda self: self.get('bookmark_time'))
  tracklen_time = property(lambda self: self.get('tracklen'))

  playcount = property(lambda self: self.get('playcount'))
  playtime = property(lambda self: self.tracklen_time - self.bookmark_time)

  # need a method that checks for podcast alias album names
  album_title = property(lambda self: self.get('album'))
  podcast_title = property(lambda self: self.album_title)

  def _conform_property(self, track, key):
    if track.get(key) is not None:
      self._set(key, track.get(key))

  def conform(self, track):
    self._conform_property(track, 'time_played')
    self._conform_property(track, 'bookmark_time')
    self._conform_property(track, 'playcount')
