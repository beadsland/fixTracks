#!/usr/bin/env python3

import os
import couchdb
import sys

root = os.path.expanduser("~/Qnap/Data/iTunes")

class Folder:
  def __init__(self, path, dict=None):
    if type(path) is str:
      self.path = path
    else:
      raise TypeError(type(path))

    if dict is None:
      self.dict = {}
    else:
      self.dict = dict
      self.iter = None

  def __str__(self):
    return "%s: %s>" % (str(type(self)).rstrip('>'), repr(self))

  def __repr__(self):
    if hasattr(self, 'iter'):
      return "<dict size %d> + %s" % (len(self.dict), repr(self.iter))
    else:
      prep = "Folder(\"%s\")" % self.path.replace(root, "%_ITUNES")
      return "<dict size %d> + %s" % (len(self.dict), prep)

  def get(self, key):
    if key in self.dict: # only retain leaves until they've been gotten
      if type(self.dict[key]) is str: return self.dict.pop(key)
      else: return self.dict[key]
    if not hasattr(self, 'iter'): self.iter = os.scandir(self.path)

    while not key in self.dict and self.iter is not None:
      sys.stdout.write("> %d in %s\r" % (len(self.dict), self.path))
      n = next(self.iter, None)
      if n is None:
        self.iter = None
      else:
        if n.is_dir():
          self.dict[n.name] = Folder(n.path)
        else:
          self.dict[n.name] = n.path

    if key in self.dict: return self.dict[key]
    raise Exception('Path Not Cached: %s' % os.path.join(self.path, key))


print("Assembling paths...")
dirs = ["iPod only", "Broadcast", "Music", "iTunes U"]
dirs = dirs + ["Podcasts%s" % (" Over"*i) for i in range(0, 4)]
dirs = {f: Folder(os.path.join(root, "iTunes Media", f)) for f in dirs}
dirs = {"Podcasts": Folder(os.path.join(root, "Podcasts")),
        "iTunes Media": Folder(os.path.join(root, "iTunes Media"), dirs)}

print(dirs)

print("\nAccessing database...")
couch = couchdb.Server("http://192.168.2.52:4000")
couch.resource.credentials = ("itunes", "senuti")
db = couch['audio_library']
for id in db:
  pref = db[id]['iTunes']['iTunes Library']['Music Folder']
  path = db[id]['iTunes']['Location'].replace(pref, "")
  print("\nSeeking %s: %s..." % (id, path))
  path = path.split('/')
  print(path)

  folder = dirs
  for p in path:
    folder = folder.get(p)
    print("⇒ %s: %s" % (p, folder))

def get_ext(f): return os.path.splitext(f)[1]
