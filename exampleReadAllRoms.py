# -*- coding: utf-8 -*-
# Copyright (c) 2011 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

import sys
import tmex
import time

def main():
    session = tmex.Session()
    devices = session.enumrate(familyFilter=[0x28])

    for key, device in tmex.iteritems(devices):
        print('%s: %s %s' % (key, device['name'], device['description']))

    while True:
        try:
            devices = list(devices)
            data = session.readDevices(devices=devices, familyFilter=['DS18B2'], timeStamp=True)
            deviceCount = 0
            for rom in data:
                if rom in devices:
                    datarom = data[rom]
                    if 'temperature' in datarom:
                        temp = datarom['temperature']
                        print("{} = {:<8} C".format(rom, temp))
                    deviceCount += 1
            if 'delta' in data:
                delta = data['delta'].total_seconds()
                print("{} sensors were surveyed for {} seconds\n".format(deviceCount, delta))
            print("Sleeping 2 seconds ...")
            time.sleep(2)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main();
