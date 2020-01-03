#!/usr/bin/env python

import savvy.ipod

print "Seeking mounted ipod..."
path = savvy.ipod.find("/media", 2)
if not path:
  print("iPod not found")
  exit()

print "Loading ipod database..."
db = savvy.ipod.load(path)

forward = sorted(db, key = lambda track: track.date_released())

print(forward[:20])
