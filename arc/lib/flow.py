# Copyright 2018 Beads Land-Trujillo

import collections
import datetime
import threading
import datetime

Event = collections.namedtuple('Event', ['time', 'size'])

class Flow:
  def __init__(self):
    self.deq = collections.deque()
    self.lock = threading.Lock()

  def append(self, evt):
    self.lock.acquire()
    self.deq.append(evt)
#    print(datetime.datetime.now() - evt.time)
    while self.deq[0].time < ( evt.time - datetime.timedelta(seconds=1) ):
      self.deq.popleft()
    self.lock.release()

  def current(self):
    self.lock.acquire()
    r = sum(int(e.size) for e in self.deq)
    self.lock.release()
    return r
