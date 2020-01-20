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
    msg = "Waiting for %s to index..." % self._viewname
    start = datetime.datetime.now()
    waiting = False
    value = None

    savvy.common.write(msg)
    while not value:
      try:
        value = func()
      except requests.exceptions.HTTPError as err:
        if 'timeout' in err.response.reason:
          delta = savvy.common.Delta(datetime.datetime.now() - start)
          savvy.common.write(' '.join([msg, str(delta)]))
          waiting = True
        else:
          raise err

    if waiting:
      print ""
    else:
      savvy.common.write("")

    return value
