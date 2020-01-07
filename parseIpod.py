#!/usr/bin/env python

import savvy

import datetime

def countholds(x, y):
  (title, rtime) = y
  x[title] = x.get(title, 0) + rtime
  return x

def savvy_roster(db, name, cap=24, history=None):
  plist = db.wipe_playlist(name)
  cap = datetime.timedelta(hours=cap)
  far = datetime.timedelta(hours=0)

  tracks = [t for t in db if not t.playcount]
  tracks = sorted(tracks, key = lambda track: track.release_date)

  import savvy.playlist
  list1 = savvy.playlist.Stagger(10, 'podcast_title', reversed(tracks))
  list2 = savvy.playlist.Stagger(10, 'podcast_title', iter(tracks))
  collate = savvy.playlist.Collate([("current", 2, savvy.playlist.Held(list1)),
                                    ("history", 1, savvy.playlist.Held(list2))])

  while collate and far < cap:
    t = next(collate)
    plist.add(t.as_libgpod)
    far = far + datetime.timedelta(milliseconds = t.playtime)
    print t

  print "%s: %d tracks" % (name, len(plist))

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
    far = far + datetime.timedelta(milliseconds = t.maxplaytime)

  print "%s: %d tracks" % (name, len(plist))

db = savvy.init("/media", "/media/removable/microSD/back")

print "Updating savvy history..."
savvy_history(db, "Savvy History")
print "Updating savvy roster..."
savvy_roster(db, "Savvy Playlist", history=db.get_playlist("Savvy History"))
