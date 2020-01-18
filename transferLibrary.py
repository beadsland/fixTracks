#!/usr/bin/env python

# Copyright 2019 Beads Land-Trujillo

print "Loading modules..."
import savvy.itunes.database
import savvy.common
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

def parseLibrary(cdb):
  seen = []
  start = datetime.datetime.now()
  count = 0
  total = cdb.doc_count()

  print "Total tracks (in couch): %d" % total

  for item in savvy.itunes.database.Database(LIBRARY):
    count += 1
    eta = (datetime.datetime.now() - start) / count * (total-count)
    eta = savvy.common.Delta(eta)

    id = item["Persistent ID"]
    cdb.update_node(id, 'iTunes', item, item["iTunes Library"]["Date"])

    seen.append(id)
    sys.stdout.write("> %2.1f%% (%d): key %s [eta %s]     \r" \
                    % (float(count)/total*100, count, item['Track ID'], eta))
  return seen

# Main routine starts here...

print "Loading couch database..."
couch = savvy.couch.Server("itunes", "senuti", COUCHDB)
db = couch["audio_library"]
mdate = datetime.datetime.fromtimestamp(os.path.getmtime(LIBRARY)).isoformat()

print "Parsing library..."
seen = parseLibrary(db)

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
