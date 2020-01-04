#!/usr/bin/env python

import savvy
db = savvy.init()

print "Building savvy playlist..."
name = "Savvy Playlist"

import savvy.ipod.database
plist = db.wipe_playlist(name)

forward = sorted(db, key = lambda track: track.date_released())

for track in forward[:10]:
  plist.add(track.as_libgpod())

print plist
