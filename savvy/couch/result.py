# Copyright 2020 Beads Land-Trujillo

import savvy.common

import datetime
import requests
import inspect

class ViewResult:
  def __init__(self, db, view, **kwargs):
    if inspect.isclass(view): view = view()
    design = '/'.join(['_design', view.design_name])
    self._result = db.get_view_result(design, view.view_name, **kwargs)
    self._viewname = view.view_name

  def __iter__(self):
    self._iter = self._wait(lambda: iter(self._result))
    return self

  def next(self):
    return self._wait(lambda: next(self._iter))

  def _wait(self, func):
    msg = "Waiting for %s..." % self._viewname
    start = datetime.datetime.now()
    waiting = False
    value = None
    task = None

    while not value:
      try:
        if not waiting: savvy.common.write(msg)
        value = func()
        if waiting: print ""
      except StopIteration:
        savvy.common.write("")
        raise StopIteration
      except requests.exceptions.HTTPError as err:
        if 'timeout' in err.response.reason:
          delta = savvy.common.Delta(datetime.datetime.now() - start)
          savvy.common.write(' '.join([msg, 'indexing...', str(delta)]))
          waiting = True
        else:
          raise err

    return value
