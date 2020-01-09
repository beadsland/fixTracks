def init(mntdir, backdir):
  print "Seeking mounted ipod..."
  import savvy.ipod
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
