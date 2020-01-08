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
  current_piles = 2
  history_piles = 1

  hold = {}
  from savvy.ipod.track import Track
  from savvy.playlist.held import Held, Delta
  if history:
    hold = [Track(t) for t in history]
    hold = [(t.podcast_title, t.maxplaytime) for t in hold]
    hold = reduce(countholds, hold, {})
    hold = {k: Delta(hold[k] * (current_piles + history_piles)) for k in hold}
    hold1 = {k: Held(timeout=hold[k]) for k in hold}
    hold2 = {k: Held(timeout=hold[k]) for k in hold}

  import savvy.playlist.stagger
  import savvy.playlist.collate
  list1 = savvy.playlist.stagger.Stagger(10, 'podcast_title', reversed(tracks),
                                                              hold=hold1)
  list2 = savvy.playlist.stagger.Stagger(10, 'podcast_title', iter(tracks),
                                                              hold=hold2)
  collate = savvy.playlist.collate.Collate([("current", current_piles, list1),
                                            ("history", history_piles, list2)])

  needle = False
  while collate and far < cap:
    print "\n%s" % collate
    t = next(collate)
    print "\n%s" % t

    if t.bookmark_time and not needle:
      plist.add(t.as_libgpod, 0)
      needle = True
    else:
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

print "\nUpdating savvy history..."
savvy_history(db, "Savvy History")
print "\nUpdating savvy roster..."
savvy_roster(db, "Savvy Playlist", history=db.get_playlist("Savvy History"))

print ""
for p in reversed(list(db.get_playlist("Savvy History"))[:5]):
  print p
sys.stdout.write("--> ")
for p in list(db.get_playlist("Savvy Playlist"))[:6]:
  print p
print ""
