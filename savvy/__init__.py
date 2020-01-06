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
  return savvy.ipod.load(path)
