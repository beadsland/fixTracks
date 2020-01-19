#!/usr/bin/env python

# Copyright 2020 Beads Land-Trujillo

print "Loading modules..."
import cloudant

import sys

COUCHDB = "http://127.0.0.1:5984/"

print "Loading couch database..."
couch = cloudant.client.CouchDB("itunes", "senuti", url=COUCHDB, connect=True)
db = couch["audio_library"]

for item in db:
  if "Persistent ID" in item['_id']:
    try:
      del(item['persist_id'])
      del(item['iTunes']['_persist_id'])
    except:
      pass
    rename = dict(item)
    rename['_id'] = rename['_id'].replace("Persistent ID ", "")
    sys.stdout.write("Renaming: %s\r" % rename['_id'])
    if db.create_document(rename):
      item.delete()

print ""
