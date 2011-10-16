# -*- coding: utf-8 -*-
# Copyright (c) 2011 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

import sys
import tmex
import time

def main():
    session = tmex.Session()
    devices = session.enumrate()

    if hex(sys.hexversion)[2:4] == '30':
        devices_iter = devices.items()
    else:
        devices_iter = devices.iteritems()        

    for key, device in devices_iter:
        print('%s: %s %s' % (key, device['name'], device['description']))

    while True:
        try:
            devices = list(devices)
            data = session.readTemperatureFromAllSensors(
                            roms=devices, timeStamp=True)
            for rom in data:
                if not rom[:2] == '28':
                    continue

                datarom = data[rom]
                temp = datarom['temperature']
                print("{} = {:<8} C".format(rom, temp))

            if 'delta' in data:
                delta = data['delta'].total_seconds()
                print("{} sensors were surveyed for {} seconds\n".format(len(devices), delta))

            print("Sleeping 2 seconds ...")
            time.sleep(2)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main();
