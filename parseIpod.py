#!/usr/bin/env python

import savvy

import datetime
import sys

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

  # Database.get_playlist() should return a savvy object, not a libgpod object
  # Doesn't yet differentiate front of list from back thereof
  hold = {}
  from savvy.ipod.track import Track
  from savvy.playlist import Held
  if history:
    hold = [Track(t) for t in history]
    hold = [(t.podcast_title, t.maxplaytime) for t in hold]
    hold = reduce(countholds, hold, {})
#    hold = {k: Held(k, timeout=v) for (k,v) in hold}
  print(hold)

  import savvy.playlist
  list1 = savvy.playlist.Stagger(10, 'podcast_title', reversed(tracks))
  collate = savvy.playlist.Collate([("current", 2, list1),
  list2 = savvy.playlist.Stagger(10, 'podcast_title', iter(tracks))
                                    ("history", 1, list2)])

  while collate and far < cap:
    print ""
    print collate
    t = next(collate)
    plist.add(t.as_libgpod)
    far = far + datetime.timedelta(milliseconds = t.playtime)

  print "\n%s: %d tracks" % (name, len(plist))

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

  print "\n%s: %d tracks" % (name, len(plist))

db = savvy.init("/media", "/media/removable/microSD/back")

print "Updating savvy history..."
savvy_history(db, "Savvy History")
print "Updating savvy roster..."
savvy_roster(db, "Savvy Playlist", history=db.get_playlist("Savvy History"))

print ""
for p in reversed(list(db.get_playlist("Savvy History"))[:5]):
  print p
sys.stdout.write("--> ")
for p in list(db.get_playlist("Savvy Playlist"))[:6]:
  print p
print ""
