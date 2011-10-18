# -*- coding: utf-8 -*-
# Copyright (c) 2011 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

import tmex

def main():
    session = tmex.Session()
    devices = session.enumrate()
     
    for key, device in tmex.iteritems(devices):
        print('%s: %s %s' % (key, device['name'], device['description']))
    
    while True:
        try:
            for key, device in tmex.iteritems(devices):
                readout = session.readDevice(key)
                if len(readout) > 0:
                    messages = ['%s:' % (key)]
                    for key, value in tmex.iteritems(readout):
                        messages.append('%s: %.2f' % (key, value))
                    print(' '.join(messages))
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main();
