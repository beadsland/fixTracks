# Copyright 2020 Beads Land-Trujillo

import savvy.couch.database
import cloudant

class Server:
  def __init__(self, user, pswd, url="http://127.0.0.1:5984/"):
    self._server = cloudant.client.CouchDB(user, pswd, url=url, connect=True,
                                           use_basic_auth=True)

  def database(self, name):
    return savvy.couch.database.Database(self._server[name])
