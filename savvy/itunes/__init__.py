# Copyright 2019 Beads Land-Trujillo

import savvy.itunes.database
import savvy.common

import datetime

def import_tracks(itunes_xml, couch_db):
  seen = []
  start = datetime.datetime.now()
  count = 0
  total = len(couch_db)

  print "Total tracks (in couch): %d" % total

  for item in savvy.itunes.database.Database(itunes_xml):
    count += 1
    eta = (datetime.datetime.now() - start) / count * (total-count)
    eta = savvy.common.Delta(eta)

    savvy.common.write("> %2.1f%% (%d): key %s [eta %s]"
                       % (float(count)/total*100, count, item['Track ID'], eta))

    id = item["Persistent ID"]
    couch_db.stage_node(id, 'iTunes', item, item["iTunes Library"]["Date"])
    seen.append(id)
  print ""
  return seen
