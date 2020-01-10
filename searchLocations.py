#!/usr/bin/env python3

# Copyright 2019 Beads Land-Trujillo

import re
import couchdb
import sys

find = sys.argv[1]

print("Seeking: %s" % find)

couch = couchdb.Server("http://192.168.2.52:4000")
couch.resource.credentials = ("itunes", "senuti")
db = couch['audio_library']
n = 0

for id in db:
  n = n + 1
  pref = db[id]['iTunes']['iTunes Library']['Music Folder']
  path = db[id]['iTunes']['Location'].replace(pref, "")
  sys.stdout.write("> %d: %s: %s          \r" % (n, id, path[:100]))

  if re.search(find, path, re.IGNORECASE):
    print("\n%s" % path)

print("\n")
