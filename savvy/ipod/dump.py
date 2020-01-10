# Copyright 2020 Beads Land-Trujillo

import savvy
#db = savvy.init("/media", "/media/removable/microSD/back").as_libgpod()

import json
import datetime
#with open("data_%s.txt" % datetime.datetime.now().isoformat(), 'w') as outfile:
#  json.dump(dump(db.Podcasts, True), outfile)

#db.close()
#exit()


def dump(obj, playlist=False):
  props = ['id', 'name', 'master', 'podcast', 'smart', 'order']

  if playlist:
    hash = {prop: getattr(obj, prop) for prop in props}
    for track in obj:
      persistid = str(track['dbid'])
      fields = {}

      for key in track:
        try:
          value = track[key]
        except:
          value = None

        import datetime
        import gpod

        if type(value) is datetime.datetime:
          fields[key] = value.isoformat()
        elif type(value) in [gpod.gpod._Itdb_iTunesDB, gpod.gpod._Itdb_Artwork]:
          pass
        elif type(value).__name__ == 'SwigPyObject':
          pass
        else:
          fields[key] = value

      if fields['playcount']:
        print fields['playcount'], track
#        track['playcount'] = int(track['playcount'] / 2)

      hash[persistid] = fields

    for key in fields:
      if fields[key] and not type(fields[key]) in [str, long, int, float, datetime.datetime]:
        print type(fields[key])

  else:
    hash = {}
    for plist in obj:
      hash[plist.name] = dump(plist, True)

  return hash
