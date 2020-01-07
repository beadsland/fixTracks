#!/usr/bin/env python

import datetime

def savvy_roster(db, name, history=None):
  plist = db.wipe_playlist(name)

  tracks = [t for t in db if not t.playcount]
  tracks = sorted(tracks, key = lambda track: track.release_date)

  import savvy.playlist
  list1 = savvy.playlist.Stagger(10, 'podcast_title', reversed(tracks))
  list2 = savvy.playlist.Stagger(10, 'podcast_title', iter(tracks))
  collate = savvy.playlist.Collate([("current", 2, savvy.playlist.Held(list1)),
                                    ("history", 1, savvy.playlist.Held(list2))])

  result = []
  for i in range(0,30):
    t = next(collate)
    print t.playcount, t.tracklen_time, t.bookmark_time, t.playtime, t
    plist.add(t.as_libgpod)

def savvy_history(db, name, cap=24):
  plist = db.wipe_playlist(name)

  cap = datetime.timedelta(hours=cap)
  far = datetime.timedelta(hours=0)

  tracks = [t for t in db if t.played]
  tracks = sorted(tracks, key = lambda track: track.get_mock_played_date(),
                          reverse = True)

  while tracks and far < cap:
    t = tracks.pop(0)
    plist.add(t.as_libgpod)
    new = (t.played * t.tracklen_time) + t.bookmark_time
    far = far + datetime.timedelta(milliseconds = new)

import savvy
db = savvy.init("/media", "/media/removable/microSD/back")

print "Updating savvy history..."
savvy_history(db, "Savvy History")
print "Updating savvy playlist..."
savvy_roster(db, "Savvy Playlist", db.get_playlist("Savvy History"))
