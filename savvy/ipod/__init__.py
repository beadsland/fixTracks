# Copyright 2020 Beads Land-Trujillo

import savvy.ipod.database
def CTRL(): return getattr(savvy.ipod.database, 'IPOD_CTRL')

import scandir
import os
import tarfile
import datetime

def init(mntdir, backdir):
  print "Seeking mounted ipod..."
  path = find(mntdir, 2)
  if not path:
    print("iPod not found")
    exit()

  print "Backing up database before touching..."
  ball(path, backdir)

  print "Loading ipod database..."
  db = load(path)

  print "Normalizing clock reset datetimes..."
  db.normalize_bad_clocktime()

  return db

# Emergency method to recover data lost by syncing with iTunes
def one_shot(db, mntdir):
  print "Seeking backup repository..."
  path = find(mntdir, 2)
  if not path:
    print("backup repository not found")
    exit()

  print "Loading backup database..."
  back = load(path)
  changed = [t for t in back if t.played_date or t.bookmark_time]
  print "Changed tracks: %d" % len(changed)

  current = db.tracks

  present = [t for t in changed if t.persist_id in current]
  print "Present on iPod: %d" % len(present)

  print "Identifying missing tracks..."
  missing = [t for t in changed if not t.persist_id in current]
  missing = sorted(missing, key=lambda t: t.release_date_sortable)
  for t in missing:
    print t.release_date, t

  print "Conforming present tracks..."
  for t in present:
    current[t.persist_id].conform(t)

def load(path):
  return savvy.ipod.database.Database(path)

def ball(path, dest = None):
  if not dest: dest = path

  now = datetime.datetime.now().isoformat()
  output = "%s_%s.tgz" % (os.path.basename(path), now)
  output = os.path.join(dest, output)

  with tarfile.open(output, "w:gz") as tar:
    folder = os.path.join(path, CTRL(), 'Device')
    tar.add(folder, arcname='Device')
    folder = os.path.join(path, CTRL(), 'iTunes')
    tar.add(folder, arcname='iTunes')

def find(dir, depth=1):
  for i in Seek(dir, depth=depth+2):
    if i.path.endswith(CTRL()):
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
