#!/usr/bin/env python

import savvy
db = savvy.init("/media", "/media/removable/microSD/back")

print "Building savvy playlist..."
name = "Savvy Playlist"

plist = db.wipe_playlist(name)

tracks = sorted(db, key = lambda track: track.release_date)
tracks = [t for t in tracks if not t.playcount]
original = reversed(tracks)

import savvy.playlist
list1 = savvy.playlist.Stagger(10, 'podcast_title', reversed(tracks))
list2 = savvy.playlist.Stagger(10, 'podcast_title', iter(tracks))

cap = 20
order = [(0, 2, list(list1)), (0, 1, list(list2))]
result = []

while len(result) < cap and len(order):
  active = order.pop(0)
  playtime = active[0]
  share = active[1]
  tracks = active[2]

  if not len(tracks): continue

  track = active[2].pop(0)
  result.append(track)
  newtime = track.playtime

  #print playtime, share, newtime, track.get('title')
  playtime = playtime + newtime/share

  order.append((playtime, share, tracks))
  order = sorted(order, key = lambda tup: tup[0])

for t in result[:20]:
  print t.playcount, t.tracklen_time, t.bookmark_time, t.playtime, t

for track in result:
  plist.add(track.as_libgpod())
