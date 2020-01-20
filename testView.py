#!/usr/bin/env python

import savvy.couch
from savvy.couch import View

class CountArtists(View):
    @staticmethod
    def map(doc):
      if 'iPod' in doc and 'artist' in doc['iPod'] and doc['iPod']['artist']:
        yield (doc['iPod']['artist'], 1)

    @staticmethod
    def reduce(keys, values, rereduce):
      return sum(values)

couch = savvy.couch.Server("itunes", "senuti")
db = couch.database("audio_library", [CountArtists()])

for item in db.view(CountArtists, group=True):
  print item
