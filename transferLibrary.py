#!/usr/bin/env python3

import os
import re
import sys
import couchdb
import json

LIBRARY = os.path.expanduser("~/Qnap/Data/iTunes/iTunes Library.xml")

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
    return key, value
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
  with open(LIBRARY, 'r') as fp:
    while True:
      line = fp.readline().strip()
      if line == "<dict>": break

    state = parseDict(fp, "<key>Tracks</key>")

    while True:
      line = fp.readline().strip()
      if line == "<dict>": break

    print("Parsing tracks...")

    while True:
      line = fp.readline().strip()
      if line == "</dict>": break
      m = re.match(r"<key>(.*)</key>", line)
      key = m.group(1)
      sys.stdout.write("> %s               \r" % key)

      line = fp.readline().strip()
      value = parseDict(fp, "</dict>")
      value['iTunes Library'] = state
      save_update(value)

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

def save_update(value):
  id = "Persistent ID %s" % value["Persistent ID"]
  doc = db.get(id, default={"_id": id})
  value["_revdate"] = value["iTunes Library"]["Date"]
  doc["iTunes"] = value
  db.save(doc)

couch = couchdb.Server("http://192.168.2.52:4000/")
couch.resource.credentials = ("itunes", "senuti")
db = couch["audio_library"]

parseLibrary(db)
