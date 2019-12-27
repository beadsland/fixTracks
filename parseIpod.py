#!/usr/bin/env python

# apt install python-gpod; unrelated to pip3 install gpod
import gpod

path = "/media/removable/IEUSER'S IP"

db = gpod.Database(path, None)

#db = gpod.Database("/media/BEADS\'S\ IPO")
#gpod.itdb_device_set_sysinfo (db._itdb.device, "ModelNumStr", "xC293");

for track in db:
  print(track['title'])
