#!/usr/bin/env python

# Copyright 2019 Beads Land-Trujillo

print "Importing modules..."
import savvy.itunes
import savvy.couch
import savvy.common.lazydict

import cloudant

import os
import datetime
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

print "Loading itunes database..."
seen = savvy.itunes.import_tracks(LIBRARY, db)

print("Marking deletions...")

class iTunesNodes(savvy.couch.View):
  @staticmethod
  def map(doc):
    if 'iTunes' in doc and '_deleted' not in doc['iTunes']:
      yield (doc['iTunes']['Date Added'], 1)

#db.sync_views([iTunesNodes])
view = savvy.common.lazydict.LazyDict(db.view(iTunesNodes), lambda x: x['id'])

for id in seen:
  if id in view:
    del(view[id])

for p in view:
  print "* %s: %s" % (p, view[p])

#for p in presume:
#  savvy.common.write("> Marking %s" % key)
#  if '_assume_deleted' in doc['iTunes']:
#    del(doc['iTunes']['_assume_deleted'])
#  print "\ndoc: %s" % doc
#  doc.save()
