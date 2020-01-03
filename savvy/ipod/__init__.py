import savvy.ipod.database

import scandir
import os

def load(path):
  return savvy.ipod.database.Database(path)

def find(dir, depth=1):
  for i in Seek("/media", depth=depth+2):
    if i.path.endswith("iPod_Control"):
      return os.path.dirname(i.path)

class Seek:
  def __init__(self, path, depth=1):
    self.path = path
    self.depth = depth

  def __iter__(self):
    self.scan = [scandir.scandir(self.path)]
    return self

  def next(self):
    try:
      item = next(self.scan[-1])
    except StopIteration:
      self.scan.pop()
      if len(self.scan):
        return next(self)
      else:
        raise StopIteration
    else:
      if item.is_dir(follow_symlinks = True):
        if len(self.scan) < self.depth:
          try:
            self.scan.append(scandir.scandir(item.path))
          except OSError as e:
            pass
          else:
            return item
        return next(self)
      else:
        return item
