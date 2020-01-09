#!/usr/bin/env python

import savvy

import datetime
import sys

def savvy_roster(db, name, cap=24, history=None):
  plist = db.wipe_playlist(name)
  cap = datetime.timedelta(hours=cap)
  far = datetime.timedelta(hours=0)

  tracks = [t for t in db if not t.playcount]
  tracks = sorted(tracks, key = lambda track: track.release_date_sortable)

  current_piles = 2
  history_piles = 1
  total_piles = current_piles + history_piles

  def span_subset_clean(tup, t):
    (incap, run, plist) = tup
    if run < incap:
      plist.append(t)
      run = run + datetime.timedelta(milliseconds = t.tracklen_time)
    return (incap, run, plist)

  def span_subset(tup, t):
    (incap, run, dict) = tup
    if run < incap:
      dict[t.podcast_title] = dict.get(t.podcast_title, 0) + t.tracklen_time
      run = run + datetime.timedelta(milliseconds = t.tracklen_time)
    return (incap, run, dict)

  ZERO_TIME = datetime.timedelta(hours = 0)

  import savvy.ipod.track
  import savvy.playlist.held
  hist = [t for t in db if t.playcount]
  hist = sorted(hist, key = lambda track: track.played_date)
  (_cap, _run, hist) = reduce(span_subset_clean, hist,
                                 (cap * total_piles, ZERO_TIME, []))
  hist2 = sorted(hist, key = lambda track: track.get_date('time_released',
                                                            True))
  hist1 = reversed(hist2)
  (_cap, _run, hist2) = reduce(span_subset, hist2,
                                 (cap * history_piles, ZERO_TIME, {}))
  (_cap, _run, hist1) = reduce(span_subset, hist1,
                                 (cap * current_piles, ZERO_TIME, {}))
  hist2 = {k: savvy.playlist.held.Held(timeout=hist2[k]) for k in hist2}
  hist1 = {k: savvy.playlist.held.Held(timeout=hist1[k]) for k in hist1}

  import savvy.playlist.stagger
  import savvy.playlist.collate
  list1 = savvy.playlist.stagger.Stagger(10, 'podcast_title', reversed(tracks),
                                                              hold=hist1)
  list2 = savvy.playlist.stagger.Stagger(10, 'podcast_title', iter(tracks),
                                                              hold=hist2)
  collate = savvy.playlist.collate.Collate([("current", current_piles, list1),
                                            ("history", history_piles, list2)])

  needle = False
  while collate and far < cap:
    print "\n%s" % collate
    t = next(collate)
    print "\n%s" % t

    if t.bookmark_time and not needle:
      plist.add(t, 0)
      needle = True
    else:
      plist.add(t)
    far = far + datetime.timedelta(milliseconds = t.playtime)

  print "\n%s: %d tracks" % (name, len(plist))

def savvy_history(db, name, cap=24):
  plist = db.wipe_playlist(name)
  cap = datetime.timedelta(hours=cap)
  far = datetime.timedelta(hours=0)

  tracks = [t for t in db if t.playcount]
  tracks = sorted(tracks, key = lambda track: track.played_date,
                          reverse = True)

  while tracks and far < cap:
    t = tracks.pop(0)
    plist.add(t)
    far = far + datetime.timedelta(milliseconds = t.tracklen_time)

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
