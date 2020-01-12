#!/usr/bin/env python

# Copyright 2019 Beads Land-Trujillo

import savvy
import savvy.messy

import sys

db = savvy.init("/media", "/media/removable/microSD/back")

print "Dropping user playlists..."
for name in db.playlists: db.drop_playlist(name)
print "\nRefreshing savvy history..."
savvy.messy.savvy_history(db, "Savvy History")
print "\nRefreshing savvy roster..."
savvy.messy.savvy_roster(db, "Savvy Playlist",
                             history=db.get_playlist("Savvy History"))

print "\nHistory: %d, Roster %d" % (len(db.get_playlist("Savvy History")),
                                    len(db.get_playlist("Savvy Playlist")) -1)

print ""
for p in reversed(list(db.get_playlist("Savvy History"))[:5]):
  print p
sys.stdout.write("--> ")
for p in list(db.get_playlist("Savvy Playlist"))[:6]:
  if p.bookmark_time:
    print "%s [%s]" % (p, savvy.common.Delta(p.bookmark_time))
  else:
    print p
