#!/usr/bin/env python

# apt install python-gpod; unrelated to pip3 install gpod
import gpod
import datetime

path = "/media/removable/IEUSER'S IP"

db = gpod.Database(path, None)

#db = gpod.Database("/media/BEADS\'S\ IPO")
#gpod.itdb_device_set_sysinfo (db._itdb.device, "ModelNumStr", "xC293");

#for track in db:
#    print hex(track['dbid']), track['time_released'], track

def time_released(track):
  try:
    return track['time_released']
  except:
    return datetime.datetime.min

forward = sorted(db, key = lambda track: time_released(track))

print(forward[:20])
