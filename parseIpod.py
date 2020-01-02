#!/usr/bin/env python

import savvy.ipod

path = "/media/removable/IEUSER'S IP"

db = savvy.ipod.Database(path)

forward = sorted(db, key = lambda track: track.date_released())

print(forward[:20])
