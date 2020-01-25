#!/usr/bin/env python

# Copyright 2019 Beads Land-Trujillo

print "Importing modules..."
import savvy.common
import savvy.ipod
import savvy.messy

import sys
import couchdb

db = savvy.ipod.init("/media", "/media/removable/microSD/back")

print "Pushing ipod records to couchdb..."

def save_update(cdb, track, mdate):
  id = track.persist_id
  doc = cdb.get(id, default={"_id": id})
  doc["iPod"] = track.dump()
  doc["iPod"]["_revdate"] = mdate
  try:
    cdb.save(doc)
  except:
    print(doc)
    exit()

couch = couchdb.Server("http://127.0.0.1:5984/")
couch.resource.credentials = ("itunes", "senuti")
cdb = couch["audio_library"]

mdate = db.modified_date.isoformat()
for track in sorted(db, key=lambda self: self.persist_id):
  savvy.common.write(' '.join(['>', track.persist_id]))
  save_update(cdb, track, mdate)
print ""

###savvy.ipod_one_shot(db, "/home/beads/Downloads")

print "Dropping user playlists..."
for name in db.playlists: db.drop_playlist(name)
db.add_playlist("Savvy Playlist")
db.add_playlist("Savvy History")

print "Refreshing savvy history..."
savvy.messy.savvy_history(db, "Savvy History", 100)
print "Refreshing savvy roster..."
savvy.messy.savvy_roster(db, "Savvy Playlist", 100,
                             history=db.get_playlist("Savvy History"))

print "History: %d, Roster %d" % (len(db.get_playlist("Savvy History")),
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
