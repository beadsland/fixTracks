#!/usr/bin/env python

# This should be an upstart script--without shared modules--but we're running
# under a chroot, so we'll just launch it from here and benefit from code
# reuse. Ultimately this would be a privileged node in a distributed Elixir
# architecture and message passing will fill in for what shared modules do here.

import savvy.ipod

import os
import psutil
import blkinfo
import usb.core
import signal
import time
import tempfile

if os.getuid():
  print "Must run daemon with sudo rights."
  exit(1)

def eject():
  # We're doing zero error checking here. Either it works or it fails badly.

  path = savvy.ipod.find("/media", 2)

  mounts = {p.mountpoint: p for p in psutil.disk_partitions()}
  mount = mounts[path].device.replace('/dev/', '')

  devices = [(d['children'], d) for d in blkinfo.BlkDiskInfo().get_disks()]
  devices = [map(lambda x: (x, dct), lst) for (lst, dct) in devices]
  devices = [item for sublist in devices for item in sublist]
  devices = {x.encode('UTF-8'): y for (x, y) in devices}

  usbdevs = {dev.serial_number: dev for dev in usb.core.find(find_all = True)}
  usbdev = usbdevs[devices[mount]['serial']]

  # This is the bit that needs to run under sudo
  usbports = '.'.join([str(n) for n in usbdev.port_numbers])
  usbdev = "%s-%s" % (usbdev.bus, usbports)
  cmd = "echo '%s' | tee /sys/bus/usb/drivers/usb/unbind > /dev/null" % usbdev
  os.system(cmd)


sema = os.path.join(tempfile.gettempdir(), "do_ipodEjectDaemon_semaphore")

while True:
  time.sleep(1)
  if os.path.exists(sema):
    try:
      eject()
      os.unlink(sema)
    except:
      pass
