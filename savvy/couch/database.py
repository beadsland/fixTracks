# Copyright 2020 Beads Land-Trujillo

class Database:
  def __init__(self, db):
    self._db = db

  def update_node(id, nade, data, revdate):
    doc = cdb[id] if id in self._db else self._db.create_document({'_id': id})
    doc[name] = data
    doc[name]['_revdate'] = revdate
    doc.save()
