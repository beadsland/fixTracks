import savvy.ipod.database

import scandir
import os
import tarfile
import datetime

def load(path):
  return savvy.ipod.database.Database(path)

def ball(path, dest = None):
  IPOD_CTRL = getattr(savvy.ipod.database, 'IPOD_CTRL')

  if not dest: dest = path

  now = datetime.datetime.now().isoformat()
  output = "%s_%s.tgz" % (os.path.basename(path), now)
  output = os.path.join(dest, output)

  with tarfile.open(output, "w:gz") as tar:
    folder = os.path.join(path, IPOD_CTRL, 'Device')
    tar.add(folder, arcname='Device')
    folder = os.path.join(path, IPOD_CTRL, 'iTunes')
    tar.add(folder, arcname='iTunes')

def find(dir, depth=1):
  IPOD_CTRL = getattr(savvy.ipod.database, 'IPOD_CTRL')

  for i in Seek("/media", depth=depth+2):
    if i.path.endswith(IPOD_CTRL):
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
