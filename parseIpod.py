#!/usr/bin/env python

import savvy
db = savvy.init("/media", "/media/removable/microSD/back")

print "Building savvy playlist..."
name = "Savvy Playlist"

plist = db.wipe_playlist(name)

tracks = sorted(db, key = lambda track: track.date_released, reverse = True)
tracks = [t for t in tracks if not t.playcount]

for t in tracks[:10]:
  print t.playcount, t.tracklen_time, t.bookmark_time, t.tracklen_time - t.bookmark_time, t

for track in tracks[:100]:
  plist.add(track.as_libgpod())

print plist
