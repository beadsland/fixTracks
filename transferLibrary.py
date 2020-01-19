#!/usr/bin/env python

# Copyright 2019 Beads Land-Trujillo

print "Importing modules..."
import savvy.itunes
import savvy.couch
import cloudant

import os
import datetime
import sys
import socket

if socket.gethostname() == "ubuntu_1804":
  COUCHDB = "http://127.0.0.1:5984/"
else:
  COUCHDB = "http://192.168.2.52:4000/"

LIBRARY = os.path.expanduser("~/Qnap/Data/iTunes/iTunes Library.xml")

print "Loading couch database..."
couch = savvy.couch.Server("itunes", "senuti", COUCHDB)
db = couch.database("audio_library")
mdate = datetime.datetime.fromtimestamp(os.path.getmtime(LIBRARY)).isoformat()

print "Parsing library..."
seen = savvy.itunes.import_tracks(LIBRARY, db)

print("\nSeen: %d" % len(seen))

print("Marking deletions... ")
presume = [doc for doc in db if 'iTunes' in doc]
#presume = [db[key] for key in db if 'iTunes' in db[key]]
print(len(presume))
presume = [doc for doc in presume if doc['iTunes']['Persistent ID'] not in seen]
print(len(presume))
presume = [doc for doc in presume if '_deleted' not in doc['iTunes']]
print(len(presume))

for p in presume:
  print("* %s: %s" % (p['_id'], p))

print ""
print ""

for doc in presume:
  sys.stdout.write("\r> Marking %s" % key)
  if '_assume_deleted' in doc['iTunes']:
    del(doc['iTunes']['_assume_deleted'])
  doc['iTunes'][u'_deleted'] = u"%s" % mdate
  print "\ndoc: %s" % doc
  doc.save()
