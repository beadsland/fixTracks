#!/usr/bin/env python

# Copyright 2019 Beads Land-Trujillo

import savvy
import savvy.messy

import sys

db = savvy.init("/media", "/media/removable/microSD/back")

print "\nUpdating savvy history..."
savvy.messy.savvy_history(db, "Savvy History")
print "\nUpdating savvy roster..."
savvy.messy.savvy_roster(db, "Savvy Playlist",
                             history=db.get_playlist("Savvy History"))

print ""
for p in reversed(list(db.get_playlist("Savvy History"))[:5]):
  print p
sys.stdout.write("--> ")
for p in list(db.get_playlist("Savvy Playlist"))[:6]:
  if p.bookmark_time:
    print "%s [%s]" % (p, savvy.common.Delta(p.bookmark_time))
  else:
    print p
print ""
