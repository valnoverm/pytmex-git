# -*- coding: utf-8 -*-
# Copyright (c) 2011 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

import ctypes
import binascii
import time
from .tmex import *

DEVICEINFO = {
    0x01: ("DS1990A", "Serial Number iButton"),
    0x10: ("DS18S2", "High-Precision 1-Wire Digital Thermometer"),
    0x26: ("DS2438", "Smart Battery Monitor"),
    0x28: ("DS18B2", "Programmable Resolution 1-Wire Digital Thermometer"),
    0x81: ("DS1420", "Serial ID Button")
}

class Session(object):
    
    def __init__(self, port=0):
        self._handle = 0
        self._context = ctypes.create_string_buffer('\000' * 15360)
        self._devices = {}
        self.initialize(port)
    
    def __del__(self):
        if self._handle != 0:
            TMEndSession(self._handle)
    
    def initialize(self, port=0):
        portNumber = ctypes.c_short(port)
        portType = ctypes.c_short(0)
        TMReadDefaultPort(portNumber, portType)
    
        self._handle = TMExtendedStartSession(portNumber, portType, None)
    
        result = TMSetup(self._handle)
        if (result != 1):
            TMEndSession(self._handle)
            if result in TMSetupMessages:
                raise TMEXException(TMSetupMessages[result])
            else:
                raise TMEXException('Unknown setup error, %d' % (result))
    
    def valid(self):
        if self._handle == 0:
            return False
        return TMValidSession(self._handle) == 1
    
    def enumrate(self, familys=[40]):
        if self._handle == 0:
            raise TMEXException('Bus not initialized')
        if not self.valid():
            raise TMEXException('Bus not valid')
        result = TMFirst(self._handle, self._context)
        devices = {}
        while result != 0:
            rom = (ctypes.c_short * 8)()
            result = TMRom(self._handle, self._context, rom)
            if result == 1:
                deviceId = ''.join(['%02X' % (x) for x in rom])
                romBytes = [x for x in rom]
                if romBytes[0] in familys:
                    rb = (ctypes.c_ubyte * 8)(*romBytes)
                    result = TMCRC(8, rb, 0, 0)
                    if result == 0:
                        kind = rom[0]
                        info = None
                        if kind in DEVICEINFO:
                            info = DEVICEINFO[kind]
                            devices[deviceId] = {'kind': kind, 'name': info[0], 'description': info[1]}
                        else:
                            devices[deviceId] = {'kind': kind}
            result = TMNext(self._handle, self._context)
        self._devices = devices
        return devices
    
    def readDevice(self, deviceId):
        if deviceId not in self._devices:
            raise ValueError()
        deviceName = self._devices[deviceId]['name']
        func = None
        try:
            func = getattr(self, '_read_' + deviceName)
        except Exception:
            func = None
        if func:
            return func(deviceId)
        else:
            return {}
    
    def _addressDevice(self, deviceId):
        if deviceId not in self._devices:
            raise ValueError()
        TMTouchReset(self._handle)
        TMTouchByte(self._handle, 0x55) # MATCH ROM
        address = [ord(x) for x in binascii.unhexlify(deviceId)]
        for i in xrange(8):
            TMTouchByte(self._handle, address[i]) # Send Id
        return 1
    
    def _read_DS18B2(self, deviceId):
        result = self._addressDevice(deviceId)
        temp = None
        if result == 1:
            TMOneWireLevel(self._handle, 0, 1, 2)
            data = TMTouchByte(self._handle, 0x44)
            time.sleep(0.6)
            data = TMTouchByte(self._handle, 0xFF)
            
            while data == 0:
                data = TMTouchByte(self._handle, 0xFF)
            TMOneWireLevel(self._handle, 0, 0, 0)
            result = self._addressDevice(deviceId)
            data = TMTouchByte(self._handle, 0xBE)
            data = [TMTouchByte(self._handle, 0xFF) for i in xrange(9)]
            temp = ((0x07 & data[1]) << 4) + ((0xF0 & data[0]) >> 4) + (((0x08 & data[0]) >> 3) * 0.5) + (((0x04 & data[0]) >> 2) * 0.25) + (((0x02 & data[0]) >> 1) * 0.125) + (((0x01 & data[0])) * 0.0625)
            if (0x08 & data[1]) == 0x08:
                temp = -temp
        return {'temperature': temp}

    def _read_DS2438(self, deviceId):
        result = self._addressDevice(deviceId)
        temp = None
        if result == 1:
            data = TMTouchByte(self._handle, 0x44)
            data = TMTouchByte(self._handle, 0xFF)
            while data == 0:
                
                data = TMTouchByte(self._handle, 0xFF)
            result = self._addressDevice(deviceId)
            data = TMTouchByte(self._handle, 0xB4)
            data = TMTouchByte(self._handle, 0xFF)
            while data == 0:
                data = TMTouchByte(self._handle, 0xFF)
            result = self._addressDevice(deviceId)
            data = TMTouchByte(self._handle, 0xB8)
            data = TMTouchByte(self._handle, 0x00)
            result = self._addressDevice(deviceId)
            data = TMTouchByte(self._handle, 0xBE)
            data = TMTouchByte(self._handle, 0x00)
            data = [TMTouchByte(self._handle, 0xFF) for i in xrange(9)]
            temp = (0x7F & data[2])
            temp += ((0x80 & data[1]) >> 7) * 0.5
            temp += ((0x40 & data[1]) >> 6) * 0.25
            temp += ((0x20 & data[1]) >> 5) * 0.125
            temp += ((0x10 & data[1]) >> 4) * 0.0625
            temp += ((0x08 & data[1]) >> 3) * 0.03125
            if (0x80 & data[2]) == 0x80:
                temp = -temp
            voltage = (((data[4] & 0x03) << 8) + (data[3])) * 0.01
            # conversion from voltage to humidity, see HIH-4021 datasheet
            humidity = ((voltage / 5.0) - 0.16) / 0.0062
            humidity = humidity / (1.0546 - (0.00216 * temp))
        return {'temperature': temp, 'humidity': humidity}
