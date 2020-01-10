# Copyright 2018 Beads Land-Trujillo

import sys
import datetime
import heapq as hq

def unplayed(gen):
  while True:
    t = next(gen)
    if t.playcount() < 1:	yield t

def collate(gen1, gen2, ratio):
  dur1 = 0
  dur2 = 0

  while True:
    if dur2 > dur1:
      t = next(gen1)
      dur1 += (t.duration() - t.bookmark()) / ratio
      sys.stdout.write("old... ")
    else:
      t = next(gen2)
      dur2 += t.duration() - t.bookmark()
      sys.stdout.write("new... ")

    yield(t)

def stagger(gen, method, ratio):
  heapq = []
  heapm = {}

  hq.heapify(heapq)

  while True:
    t = next(gen)
    k = getattr(t, method)()

    if k in heapm:                  # Append on existing timer
      heapm[k].append(t)
    else:                           # Create new timer
      heapm[k] = [t]
      item = ( 0, datetime.datetime.now(), k )
      hq.heappush(heapq, item)

    if heapq[0][0] > 0:   continue  # No timers expired

    pop = hq.heappop(heapq)
    k = pop[2]
    if not k in heapm:    continue  # Timer has no current deferrals

    t = heapm[k].pop()
    if not heapm[k]:                # Empty list, delete list
      del heapm[k]

      item = ( ratio * (t.duration() - t.bookmark()), datetime.datetime.now(), k )
      hq.heappush(heapq, item)

    newq = []
    hq.heapify(heapq)

    for item in heapq:
      if item[2] is k:
        hq.heappush(newq, item)
      else:
        nitem = ( item[0] - (t.duration() - t.bookmark()), item[1], k )
        hq.heappush(newq, nitem)
    heapq = newq

    print heapq
    print heapm
    print " "

    yield t
