#!/usr/bin/env python

import savvy.ipod

import datetime

path = "/media/removable/IEUSER'S IP"

db = savvy.ipod.Database(path)

def time_released(track):
  try:
    return track['time_released']
  except:
    return datetime.datetime.min

forward = sorted(db, key = lambda track: time_released(track))

print(forward[:20])
