#!/usr/bin/env python

print "Seeking mounted ipod..."
import savvy.ipod
path = savvy.ipod.find("/media", 2)
if not path:
  print("iPod not found")
  exit()

print "Backing up database before touching..."
savvy.ipod.ball(path, "/media/removable/microSD/back")

print "Loading ipod database..."
db = savvy.ipod.load(path)

print "Building savvy playlist..."
title = "Savvy Playlist"

if title not in db.playlists():
  db.add_playlist(title)

plist = db.playlists()[title]

for track in reversed(plist):
  print "Removing: %s" % str(track)
  plist.remove(track)

forward = sorted(db, key = lambda track: track.date_released())

for track in forward[:20]:
  plist.add(track.as_libgpod())

print db.playlists()

print len(plist), plist
