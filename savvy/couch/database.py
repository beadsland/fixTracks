# Copyright 2020 Beads Land-Trujillo

import couchdb

import itertools
import sys
import inspect

class Database:
  def __init__(self, db, viewdb, views):
    self._db = db
    self._viewdb = viewdb
    self._bulk = {}
    self._flywheel = itertools.cycle("/-\|")
    if views: self.sync_views(views)

  def sync_views(self, views):
    views = [view() if inspect.isclass(view) else view for view in views]
    # This is legacy entry point, derived from Haase's python view
    # implementation. Ideally, we ought to do the same thing only using
    # cloudant library, and abandon dependency on now defunct couchdb library.
    couchdb.design.ViewDefinition.sync_many(self._viewdb, views,
                                            remove_missing=True)

  # Bug: https://github.com/cloudant/python-cloudant/issues/456
  def view(self, view, **kwargs):
    if inspect.isclass(view): view = view()
    self.flush()

    design = '/'.join(['_design', view.design_name])
    return self._db.get_view_result(design, view.view_name, **kwargs)

  def __len__(self):
    return self._db.doc_count()

  def __iter__(self):
    self.flush()
    return iter(self._db)

  def get_docs(self, ids):
    cache = self._db.all_docs(keys=ids, include_docs=True)['rows']
    for row in cache:
      if 'doc' not in row:
        row['id'] = row['key']
        row['doc'] = {'_id': row['key']}
    return {row['id']: row['doc'] for row in cache}

  def __del__(self):
    if len(self._bulk):
      print "Bulk updating %d documents...%s" % (len(self._bulk), " "*10)
      self.flush()
      print "Bulk update finished"

  def flush(self):
    for i in range(0, 3):
      if len(self._bulk): self._push_bulk()
    if len(self._bulk):
      ids = ", ".join(self._bulk.keys())
      msg = ': '.join(["%d documents not updating: " % len(self._bulk), ids])
      raise BufferError(msg)

  def stage_node(self, id, key, value, revdate):
    if not key in self._bulk: self._bulk[id] = []
    value['_revdate'] = revdate
    self._bulk[id].append((key, value))
    if len(self._bulk) >= 500: self._push_bulk()

  def _push_bulk(self):
    cache = self.get_docs(self._bulk.keys())
    bulk = [self._collate_nodes(id, self._bulk[id], cache) for id in self._bulk]
    for resp in self._db.bulk_docs(bulk): self._parse_bulk_response(resp)
    if len(self._bulk): print "Conflicts left %d documents" % len(self._bulk)

  def _parse_bulk_response(self, resp):
    if 'ok' in resp and resp['ok']:
      self._bulk.pop(resp['id'])
    elif 'error' in resp:
      if resp['error'] == 'conflict': return
      msg = ': '.join(['bulk docs', resp['error'], resp['reason'], resp['id'],
                       bulk[resp['id']]])
      if resp['error'] == 'forbidden': raise ValueError(msg)
      raise IOError(msg)

  def _collate_nodes(self, id, nodes, cache):
    sys.stdout.write("%s\r" % next(self._flywheel))

    doc = cache[id] if id in cache else {}
    dnodes = [(key, doc[key]) for key in doc
                                      if key not in ('_id', '_rev', '_deleted')]
    nodes = dnodes + nodes
    dels = [value for (key, value) in nodes if key == '_deleted']
    nodes = sorted(nodes, key=lambda (k,v): v['_revdate'])
    nodes = {key: value for (key, value) in nodes}

    nodes['_id'] = id
    if '_rev' in doc: nodes['_rev'] = doc['_rev']
    if len(dels): nodes['_deleted'] = dels[-1]
    return nodes
