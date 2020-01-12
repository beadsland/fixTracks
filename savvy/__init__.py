# Copyright 2020 Beads Land-Trujillo

import savvy.ipod

def init(mntdir, backdir):
  print "Seeking mounted ipod..."
  path = savvy.ipod.find(mntdir, 2)
  if not path:
    print("iPod not found")
    exit()

  print "Backing up database before touching..."
  savvy.ipod.ball(path, backdir)

  print "Loading ipod database..."
  db = savvy.ipod.load(path)

  print "Normalizing clock reset datetimes..."
  db.normalize_bad_clocktime()

  return db

# Emergency method to recover data lost by syncing with iTunes
def one_shot(db, mntdir):
  print "Seeking backup repository..."
  path = savvy.ipod.find(mntdir, 2)
  if not path:
    print("backup repository not found")
    exit()

  print "Loading backup database..."
  back = savvy.ipod.load(path)
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
