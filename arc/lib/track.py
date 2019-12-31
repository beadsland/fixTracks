def generate(playlist):
  return (Track(t) for t in playlist)

class Track:
  def __init__(self, data):	self.data = data

  def duration(self):		return float(self.data['tracklen']) / 1000
  def bookmark(self):		return float(self.data['bookmark_time']) / 1000
  def playcount(self):		return self.data['playcount']

  def title(self):		return self.data['title']
  def album(self):		return self.data['album']
  def artist(self):		return self.data['artist']

  def __str__(self):
    if self.playcount() < 1:
      frac = str(int(self.bookmark())) + "/" + str(int(self.duration()))
    else:
      frac = str(self.playcount()) + "x"

    return "%10s | %s" % (frac, self.desc())

  def desc(self):
    return "%-10s | %-10s | %-50s" % (self.album()[:10], self.artist()[:10], self.title()[:50])
