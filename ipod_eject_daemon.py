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

# Detach not enough, need to unbind
#usbdev.detach_kernel_driver(0)

# This only works with sudo -- so we're gonna need a service to do it.
#usbports = '.'.join([str(n) for n in usbdev.port_numbers])
#usbdev = "%s-%s" % (usbdev.bus, usbports)
# system call: echo '1-1'| tee /sys/bus/usb/drivers/usb/unbind
