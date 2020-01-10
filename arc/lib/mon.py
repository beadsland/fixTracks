#!/usr/bin/env python3.6

# Copyright 2018 Beads Land-Trujillo

import lib.flow
import pyshark
import threading
import datetime

capture = pyshark.LiveCapture(interface='usbmon2')
flout = lib.flow.Flow()
flin = lib.flow.Flow()

def sniffer():
  for packet in capture.sniff_continuously():
    if int(packet.usb.endpoint_number_direction) == 0:
      flout.append(lib.flow.Event(packet.sniff_time, packet.usb.data_len))
      flin.append(lib.flow.Event(packet.sniff_time, 0))
    else:
      flin.append(lib.flow.Event(packet.sniff_time, packet.usb.data_len))
      flout.append(lib.flow.Event(packet.sniff_time, 0))

def heartbeat():
  while 1:
    ping = datetime.datetime.now() - datetime.timedelta(seconds=10)
    flout.append(lib.flow.Event(ping, 0))
    flin.append(lib.flow.Event(ping, 0))


threading.Thread(target=sniffer).start()
threading.Thread(target=heartbeat).start()
