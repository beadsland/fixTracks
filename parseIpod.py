#!/usr/bin/env python

import psutil
mounts = {p.mountpoint: p for p in psutil.disk_partitions()}
mount = mounts['/media/beads/IEUSER\'S IP'].device.replace('/dev/', '')

import blkinfo
devices = [(d['children'], d) for d in blkinfo.BlkDiskInfo().get_disks()]
devices = [map(lambda x: (x, dct), lst) for (lst, dct) in devices]
devices = [item for sublist in devices for item in sublist]
devices = {x.encode('UTF-8'): y for (x, y) in devices}

import usb.core
usbdevs = {dev.serial_number: dev for dev in usb.core.find(find_all = True)}
usbdev = usbdevs[devices[mount]['serial']]
#usbports = '.'.join([str(n) for n in usbdev.port_numbers])
#usbdev = "%s-%s" % (usbdev.bus, usbports)
usbdev.detach_kernel_driver(0)





exit()


import savvy
db = savvy.init()

print "Building savvy playlist..."
name = "Savvy Playlist"

import savvy.ipod.database
plist = db.wipe_playlist(name)

forward = sorted(db, key = lambda track: track.date_released())

for track in forward[:10]:
  plist.add(track.as_libgpod())

print plist
