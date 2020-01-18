#!/usr/bin/env python

from vend.couchview import CouchView

class CountArtists(CouchView):
    @staticmethod
    def map(doc):
      if 'iPod' in doc and 'artist' in doc['iPod'] and doc['iPod']['artist']:
        yield (doc['iPod']['artist'], 1)

    @staticmethod
    def reduce(keys, values, rereduce):
      return sum(values)

couch_views = [
    CountArtists(),
    # Put other view classes here
]

import couchdb
couch = couchdb.Server()
db = couch['audio_library']
db.resource.credentials = ('itunes', 'senuti')
print couchdb.design.ViewDefinition.sync_many(db, couch_views, remove_missing=True)

for item in db.view('/'.join(['_design', __name__, '_view', 'count_artists']), group=True):
  print item.key, item.value
