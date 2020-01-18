# Copyright 2019 Beads Land-Trujillo

import savvy.itunes.database
import savvy.common

import datetime

def import(itunes_xml, couch_db):
  seen = []
  start = datetime.datetime.now()
  count = 0
  total = couch_db.doc_count()

  print "Total tracks (in couch): %d" % total

  for item in savvy.itunes.database.Database(itunes_xml):
    count += 1
    eta = (datetime.datetime.now() - start) / count * (total-count)
    eta = savvy.common.Delta(eta)

    id = item["Persistent ID"]
    couch_db.update_node(id, 'iTunes', item, item["iTunes Library"]["Date"])

    seen.append(id)
    sys.stdout.write("> %2.1f%% (%d): key %s [eta %s]     \r" \
                     % (float(count)/total*100, count, item['Track ID'], eta))
  return seen
