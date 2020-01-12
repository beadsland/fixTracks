#!/usr/bin/env python

# Copyright 2019 Beads Land-Trujillo

print "Importing modules..."

import savvy
import savvy.messy

import sys

db = savvy.init("/media", "/media/removable/microSD/back")

###savvy.one_shot(db, "/home/beads/Downloads")

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
for t in reversed(list(db.get_playlist("Savvy History"))[:5]):
  print t
sys.stdout.write("--> ")
for t in list(db.get_playlist("Savvy Playlist"))[:6]:
  if t.bookmark_time:
    print "%s [%s]" % (t, savvy.common.Delta(t.bookmark_time))
  else:
    print t
print ""
