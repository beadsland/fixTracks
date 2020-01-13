#!/usr/bin/env python3

# Copyright 2019 Beads Land-Trujillo

import os
import re
import sys
import couchdb
import html
import urllib
import datetime

LIBRARY = os.path.expanduser("~/Qnap/Data/iTunes/iTunes Library.xml")

def is_int(v):
  try: int(v)
  except ValueError: return False
  else: return True

def is_float(v):
  if len(v) >= 16: return False
  try: float(v)
  except ValueError: return False
  else: return float(v) != float("inf")

def parseKeyValue(fp, line):
  m = re.match(r"<key>(.*)</key>(.*)", line)
  key = m.group(1)
  value = m.group(2)
  if value == "<true/>": return key, True
  if value == "<false/>": return key, False

  while not re.search("</[^>]+>", value):
    more = fp.readline().strip()
    if more == "<array>": return key, parseArray(fp)
    if more == "<data>": return key, parseData(fp, "<data>")
    value = "%s\n%s" % (value, more)
  n = re.match(r"<[^>]+>([^<]+)</[^>]+>", value)
  if n is not None:
    value = n.group(1)
    if is_int(value): return key, int(value)
    if is_float(value): return key, float(value)
    return key, urllib.parse.unquote(html.unescape(value))
  else:
    print("fail: %s" % value)
    exit()

def parseData(fp, value):
  while not re.search("</[^>]+>", value):
    more = fp.readline().strip()
    value = "%s\n%s" % (value, more)
  n = re.match(r"<data>([^<]+)</data>", value)
  return "data(%s)" % n.group(1).strip()

def parseArray(fp):
  arr = []
  while True:
    line = fp.readline().strip()
    if line == "</array>": break
    if line == "<dict>":
      dict = parseDict(fp, "</dict>")
      if "Name" in dict: print(dict["Name"])
      arr.append(dict)
  return arr

def parseDict(fp, next):
  dict = {}
  while True:
    line = fp.readline().strip()
    if line == next: break
    else:
      k, v = parseKeyValue(fp, line)
      if k in dict:
        if type(dict[k]) is not list: dict[k] = [dict[k]]
        dict[k].append(v)
      else:
        dict[k] = v
  return dict

def parseLibrary(db):
  seen = []
  with open(LIBRARY, 'r') as fp:
    while True:
      line = fp.readline().strip()
      if line == "<dict>": break

    state = parseDict(fp, "<key>Tracks</key>")

    while True:
      line = fp.readline().strip()
      if line == "<dict>": break

    print("Pushing tracks from itunes xml to couchdb...")

    count = 0
    while True:
      line = fp.readline().strip()
      if line == "</dict>": break
      m = re.match(r"<key>(.*)</key>", line)
      key = m.group(1)
      count += 1
      sys.stdout.write("> %d: key %s          \r" % (count, key))

      line = fp.readline().strip()
      value = parseDict(fp, "</dict>")
      value['iTunes Library'] = state
      save_update(db, value)
      seen.append(value['Persistent ID']) # _persist_id

    line = fp.readline().strip()
    if line == "<key>Playlists</key>":
      print("\nDiscarding playlists...")
      line = fp.readline().strip()
      if line == "<array>": print(len(parseArray(fp)))
      if line != "<array>": print("huh: %s" % line)

    while True:
      line = fp.readline().strip()
      if not line: break
      print(line)

  return seen

def save_update(db, node):
  node["_persist_id"] = node["Persistent ID"]
  id = "Persistent ID %s" % node["_persist_id"]
  doc = db.get(id, default={"_id": id})

  node["_revdate"] = node["iTunes Library"]["Date"]
  doc["iTunes"] = node
  db.save(doc)

# Main routine starts here...

couch = couchdb.Server("http://192.168.2.52:4000/")
couch.resource.credentials = ("itunes", "senuti")
db = couch["audio_library"]
mdate = datetime.datetime.fromtimestamp(os.path.getmtime(LIBRARY)).isoformat()
seen = parseLibrary(db)

print("\nMarking presumptive deletions... ")
presume = [doc for doc in couch if 'iTunes' in doc]
presume = [doc for doc in presume if '_persist_id' not in doc['iTunes']
                                  or doc['iTunes']['_persist_id'] not in seen]
presume = [doc for doc in presume if '_persist_id' not in doc['iTunes']
                                  or '_deleted' not in doc['iTunes']]

print(presume)

for doc in presume:
  key = doc['iTunes']['Persistent ID']
  sys.stdout.write("\r> Marking %s" % key)
  doc['iTunes']['_persist_id'] = key
  del(doc['iTunes']['_assume_deleted'])
  doc['iTunes']['_deleted'] = mdate
  db.save(db, doc)
