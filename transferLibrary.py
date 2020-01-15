#!/usr/bin/env python

# Copyright 2019 Beads Land-Trujillo

print "Loading modules..."
import savvy.itunes.database
import savvy.common
import couchdb

import os
import datetime
import sys

LIBRARY = os.path.expanduser("~/Qnap/Data/iTunes/iTunes Library.xml")

def parseLibrary(cdb):
  seen = []
  start = datetime.datetime.now()
  count = 0
  total = len(cdb)

  for item in savvy.itunes.database.Database(LIBRARY):
    count += 1
    eta = (datetime.datetime.now() - start) / count * (total-count)
    eta = savvy.common.Delta(eta)

    save_update(cdb, item)
    seen.append(item['_persist_id'])

    sys.stdout.write("> %2.1f%% (%d): key %s [eta %s]     \r" \
                    % (count/total*100, count, item['Track ID'], eta))

  return seen

def save_update(db, node):
  node["_persist_id"] = node["Persistent ID"]
  id = "Persistent ID %s" % node["_persist_id"]
  doc = db.get(id, default={"_id": id})

  node["_revdate"] = node["iTunes Library"]["Date"]
  doc["iTunes"] = node
  doc["persist_id"] = node["_persist_id"]
  db.save(doc)

# Main routine starts here...

print "Loading couch database..."
couch = couchdb.Server("http://192.168.2.52:4000/")
couch.resource.credentials = ("itunes", "senuti")
db = couch["audio_library"]
mdate = datetime.datetime.fromtimestamp(os.path.getmtime(LIBRARY)).isoformat()

print "Parsing library..."
seen = parseLibrary(db)

#seen = [db[key] for key in db if '_assume_deleted' not in db[key]['iTunes']]
#seen = [doc['iTunes']['_persist_id'] for doc in seen]
print(len(seen))

print("\nMarking deletions... ")
presume = [db[key] for key in db if 'iTunes' in db[key]]
print(len(presume))
presume = [doc for doc in presume if doc['iTunes']['Persistent ID'] not in seen]
print(len(presume))
presume = [doc for doc in presume if '_deleted' not in doc['iTunes']]
print(len(presume))

for p in presume:
  print("* %s: %s" % (p['_id'], p))

for doc in presume:
  key = doc['iTunes']['Persistent ID']
  sys.stdout.write("\r> Marking %s" % key)
  doc['iTunes']['_persist_id'] = key
  doc['persist_id'] = key
  if '_assume_deleted' in doc['iTunes']:
    del(doc['iTunes']['_assume_deleted'])
  doc['iTunes']['_deleted'] = mdate
  db.save(doc)
