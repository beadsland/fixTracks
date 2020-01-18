#!/usr/bin/env python3

# Copyright 2019 Beads Land-Trujillo

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

  def __iter__(self):
    return self

  def __next__(self):
    if not hasattr(self, 'iter'): self.iter = os.scandir(self.path)
    while self.iter or self.dict:
      while len(self.dict):
        key = list(self.dict.keys())[0]
        result = self._next_deep(key)
        if result: return os.path.join(self.path, result)
        self.dict.pop(key)
      self._get_push(next(self.iter))
    raise StopIteration

  def _next_deep(self, key):
    if type(self.dict[key]) is str:
      return self.dict.pop(key)
    else:
      folder = self.dict[key]
      try:
        return os.path.join(key, next(folder))
      except:
        return None

  def get(self, key):
    if key in self.dict: # only retain leaves until they've been gotten
      if type(self.dict[key]) is str: return self.dict.pop(key)
      else: return self.dict[key]
    if not hasattr(self, 'iter'): self.iter = os.scandir(self.path)

    while not key in self.dict and self.iter is not None:
      sys.stdout.write("> %d in %s\r" % (len(self.dict), self.path))
      self._get_push(next(self.iter))

    if key in self.dict: return self.dict[key]
    raise Exception('Path Not Cached: %s' % os.path.join(self.path, key))

  def _get_push(self, n):
    self.dict[n.name] = Folder(n.path) if n.is_dir() else n.path

def assemble_paths():
  print("Assembling paths...")
  dirs = ["Downloads", "iPod only", "Broadcast", "Music"]
  dirs = dirs + ["Podcasts%s" % (" Over"*i) for i in range(0, 4)]
  dirs = {f: Folder(os.path.join(root, "iTunes Media", f)) for f in dirs}
  dirs["iTunes U"] = dirs["Podcasts"]  # This one's a softlink
  dirs = {"Podcasts": Folder(os.path.join(root, "Podcasts")),
          "iTunes Media": Folder(os.path.join(root, "iTunes Media"), dirs)}
  return dirs

def match_tracks(dirs):
  print("\nAccessing database...")
  couch = couchdb.Server("http://192.168.2.52:4000")
  couch.resource.credentials = ("itunes", "senuti")
  db = couch['audio_library']
  for id in db:
    if '_deleted' in db[id]['iTunes']: continue
    if db[id]['iTunes']['Track Type'] == "URL": continue
    if db[id]['iTunes']['Location'].startswith("file://localhost/N:/Torrents/"): continue

    pref = db[id]['iTunes']['iTunes Library']['Music Folder']
    path = db[id]['iTunes']['Location'].replace(pref, "")
    print("\nSeeking %s: %s..." % (id, path))
    path = path.split('/')
    print(path)

    folder = dirs
    for p in path:
      folder = folder.get(p)
      print("⇒ %s: %s" % (p, folder))

dirs = assemble_paths()
match_tracks(dirs)

print("Traverse remaining files...")
i = 0
for d in dirs:
  for f in dirs[d]:
    i += 1
    print(i, f)



def get_ext(f): return os.path.splitext(f)[1]
