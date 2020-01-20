# Copyright 2020 Beads Land-Trujillo

import savvy.couch.database
from vend.couchview import CouchView
import cloudant
import couchdb
import inspect_mate

class Server:
  def __init__(self, user, pswd, url="http://127.0.0.1:5984/"):
    self._server = cloudant.client.CouchDB(user, pswd, url=url, connect=True,
                                           use_basic_auth=True)
    self._viewserver = couchdb.Server(url)
    self._viewserver.resource.credentials = (user, pswd)

  def database(self, name, views=None):
    return savvy.couch.database.Database(self._server[name],
                                         self._viewserver[name], views)

class View(CouchView):
  def __init__(self):
    if not inspect_mate.is_static_method(self.__class__, 'map'):
      raise SyntaxError(': '.join(['must be static method', 'map']))
    if hasattr(self, 'reduce'):
      if not inspect_mate.is_static_method(self.__class__, 'reduce'):
        raise SyntaxError(': '.join(['must be static method', 'reduce']))

    super(View, self).__init__()
