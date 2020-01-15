#!/usr/bin/env python

# Copyright 2019 Beads Land-Trujillo

print "Importing modules..."
import savvy.ipod
import savvy.messy

import sys
import couchdb

db = savvy.ipod.init("/media", "/media/removable/microSD/back")

print "Pushing ipod records to couchdb..."

def save_update(cdb, track, mdate):
  id = "Persistent ID %s" % track.persist_id
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
  sys.stdout.write("\r> %s  " % track.persist_id)
  save_update(cdb, track, mdate)
print ""

###savvy.ipod_one_shot(db, "/home/beads/Downloads")

print "\nDropping user playlists..."
for name in db.playlists: db.drop_playlist(name)
db.add_playlist("Savvy Playlist")
db.add_playlist("Savvy History")

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
