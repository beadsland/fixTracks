#!/usr/bin/env python

import savvy
db = savvy.init("/media", "/media/removable/microSD/back")

print "Building savvy playlist..."
name = "Savvy Playlist"

plist = db.wipe_playlist(name)

tracks = sorted(db, key = lambda track: track.release_date)
tracks = [t for t in tracks if not t.playcount]

import savvy.playlist
list1 = savvy.playlist.Stagger(10, 'podcast_title', reversed(tracks))
list2 = savvy.playlist.Stagger(10, 'podcast_title', iter(tracks))
collate = savvy.playlist.Collate([("current", 2, savvy.playlist.Held(list1)),
                                  ("history", 1, savvy.playlist.Held(list2))])

result = []
for i in range(0,30):
  t = next(collate)
  print t.playcount, t.tracklen_time, t.bookmark_time, t.playtime, t
  plist.add(t.as_libgpod())
