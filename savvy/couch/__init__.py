# Copyright 2020 Beads Land-Trujillo

class Server:
  def __init__(self, user, pass, url="http://127.0.0.1:5984/")
    self._server = cloudant.client.CouchDB(self, user, url=url, connect=True)

  def database(name):
    return savvy.couch.database.Database(self._server[name])
