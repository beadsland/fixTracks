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

print db.playlists()

if "Podcasts" in db.playlists():
  print "There!"
  
if "Savvy Playlist" not in db.playlists():
  print "Not there!"

#forward = sorted(db, key = lambda track: track.date_released())

#print(forward[:20])
