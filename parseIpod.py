#!/usr/bin/env python

import savvy
db = savvy.init("/media", "/media/removable/microSD/back")

print "Building savvy playlist..."
name = "Savvy Playlist"

plist = db.wipe_playlist(name)

tracks = sorted(db, key = lambda track: track.date_released)
tracks = [t for t in tracks if not t.playcount]
original = reversed(tracks)

order = [(0, 3, list(reversed(tracks))), (0, 1, tracks)]
result = []

while len(result) < 100 and len(order):
  active = order.pop(0)
  playtime = active[0]
  share = active[1]
  tracks = active[2]
  print playtime, share,

  if not len(tracks): continue

  track = active[2].pop()
  result.append(track)
  newtime = track.tracklen_time - track.bookmark_time

  print playtime, share, newtime, track.get('title')
  playtime = playtime + newtime*share

  order.append((playtime, share, tracks))
  order = sorted(order, key = lambda tup: tup[0])

for t in result[:20]:
  print t.playcount, t.tracklen_time, t.bookmark_time, t.tracklen_time - t.bookmark_time, t

for track in result:
  plist.add(track.as_libgpod())
