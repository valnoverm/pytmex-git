# -*- coding: utf-8 -*-
# Copyright (c) 2011 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

import ctypes
import time
from .tmex import *
from .system import ISPYTHON3, iteritems
from datetime import datetime

if not ISPYTHON3:
    import binascii

DEVICEINFO = {
    0x01: ("DS1990A", "Serial Number iButton"),
    0x10: ("DS18S2", "High-Precision 1-Wire Digital Thermometer"),
    0x26: ("DS2438", "Smart Battery Monitor"),
    0x28: ("DS18B2", "Programmable Resolution 1-Wire Digital Thermometer"),
    0x81: ("DS1420", "Serial ID Button")
}

class Session(object):
    """
    Session is a class that encapsulates a 1-Wire session.
    """

    def __init__(self, port=0):
        """
        Initializes a 1-Wire session.
        
        port:
            A optional port number that will be used to start the session.
        """
        self._handle = 0
        if ISPYTHON3:
            self._context = ctypes.create_string_buffer(b'\000' * 15360)
        else:
            self._context = ctypes.create_string_buffer('\000' * 15360)
        self._devices = {}
        self.initialize(port)

    def __del__(self):
        if self._handle != 0:
            TMEndSession(self._handle)

    def initialize(self, port=0):
        """
        Initializes a 1-Wire session.
        
        port:
            A optional port number that will be used to start the session.
        """
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
        """
        Check if the 1-Wire session is valid.
        """
        if self._handle == 0:
            return False
        return TMValidSession(self._handle) == 1
    
    def _deviceFilter(self, devices, familyFilter):
        """
        Filter devices by family.
        
        devices:
            A list of device identifiers.
        
        familyFilter:
            A list of integers or strings where integers are the device family code and strings is the device family
            name.
        
        returns a list of device identifiers.
        """
        result = []
        filterNumbers = []
        for family in familyFilter:
            if isinstance(family, (int)):
                filterNumbers.append(family)
            elif isinstance(family, (str)):
                found = False
                for num, info in iteritems(DEVICEINFO):
                    if family == info[0]:
                        filterNumbers.append(num)
                        found = True
                        break
                if not found:
                    raise TMEXException('Unknown device {}'.format(family))
        if not filterNumbers:
            return devices
        for deviceId in devices:
            code = int(deviceId[:2], 16)
            if code in filterNumbers:
                result.append(deviceId)
        return result

    def enumrate(self, familyFilter=None):
        """
        Enumerates the devices on the 1-Wire bus.
        
        familyFilter:
            A optional list of family codes for devices to enumerate, omitting any device of a family not found in the
            list.
        """
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
                deviceId = ''.join(['%02X' % x for x in rom])
                romBytes = [x for x in rom]
                rb = (ctypes.c_ubyte * 8)(*romBytes)
                result = TMCRC(8, rb, 0, 0)
                if result == 0:
                    kind = int(rom[0])
                    info = None
                    if kind in DEVICEINFO:
                        info = DEVICEINFO[kind]
                        devices[deviceId] = {'kind': kind, 'name': info[0], 'description': info[1]}
                    else:
                        devices[deviceId] = {'kind': kind}
            result = TMNext(self._handle, self._context)
        self._devices = devices
        filteredDevices = {}
        if familyFilter:
            ids = self._deviceFilter(devices.keys(), familyFilter)
            for deviceId in ids:
                filteredDevices[deviceId] = devices[deviceId]
        else:
            filteredDevices = devices
        return filteredDevices

    def readDevice(self, deviceId, enableWireLeveling=False):
        """
        Reads the value from a device on the 1-Wire bus.
        
        deviceId:
            The device id of the device to read. Must have been enumerated.
        
        enableWireLeveling:
            Enables the reader to use wire leveling to read from certain devices.
        """
        if deviceId not in self._devices:
            raise ValueError()
        deviceName = self._devices[deviceId]['name']
        func = None
        try:
            func = getattr(self, '_read_' + deviceName)
        except AttributeError:
            func = None
        if func:
            return func(deviceId, enableWireLeveling)
        else:
            return {}

    def readDevices(self, devices, familyFilter=None, timeStamp=True):
        """
        Reads the value from a list of devices from the 1-Wire bus.
        
        devices:
            A list of device id of the devices to read. Must have been enumerated.
        
        familyFilter:
            A optional list of integers or strings where integers are the device family code and strings is the device
            family name.
        
        timeStamp:
            A optional boolean to enable value timestamps and request timing.
        """
        if familyFilter:
            devices = self._deviceFilter(devices, familyFilter)
        if len(devices) == 0:
            return {}
        if timeStamp:
            startTime = datetime.now()

        TMTouchReset(self._handle)
        TMOneWireLevel(self._handle, 0, 1, 2)

        TMTouchByte(self._handle, 0xCC)
        TMTouchByte(self._handle, 0x44)

        time.sleep(.750)
        data = TMTouchByte(self._handle, 0xFF)

        while data == 0:
            data = TMTouchByte(self._handle, 0xFF)

        TMOneWireLevel(self._handle, 0, 0, 0)
        result = {}

        for deviceId in devices:
            t = self.readDevice(deviceId, enableWireLeveling=False)
            result[deviceId] = {}
            for key, value in iteritems(t):
                result[deviceId][key] = value
            if timeStamp:
                result[deviceId]['timestamp'] = datetime.now()

        if timeStamp:
            stopTime = datetime.now()
            result['time'] = (startTime, stopTime)
            result['delta'] = stopTime - startTime
        return result

    def _addressDevice(self, deviceId):
        """
        Addresses a device on the 1-Wire bus directly.
        
        deviceId:
            The device id of the device to read. Must have been enumerated.
        """
        if deviceId not in self._devices:
            raise ValueError()
        TMTouchReset(self._handle)
        TMTouchByte(self._handle, 0x55) # MATCH ROM
        if ISPYTHON3:
            # FIXME: Bad code
            address = [ord(chr(x)) for x in bytes.fromhex(deviceId) ]
        else:
            address = [ord(x) for x in binascii.unhexlify(deviceId)]
        for i in range(8):
            TMTouchByte(self._handle, address[i]) # Send Id
        return 1

    def _read_DS18B2(self, deviceId, enableWireLeveling=False):
        """
        Reads the value from a DS18B2 device on the 1-Wire bus.
        
        deviceId:
            The device id of the device to read. Must have been enumerated.
        
        enableWireLeveling:
            Enables the reader to use wire leveling to read from certain devices.
        """
        result = self._addressDevice(deviceId)
        temp = None
        if result == 1:
            if enableWireLeveling:
                TMOneWireLevel(self._handle, 0, 1, 2)
                data = TMTouchByte(self._handle, 0x44)
                time.sleep(0.6)
                data = TMTouchByte(self._handle, 0xFF)
                while data == 0:
                    data = TMTouchByte(self._handle, 0xFF)
                TMOneWireLevel(self._handle, 0, 0, 0)
            result = self._addressDevice(deviceId)
            data = TMTouchByte(self._handle, 0xBE)
            data = [TMTouchByte(self._handle, 0xFF) for i in range(9)]
            temp = ((0x07 & data[1]) << 4) + ((0xF0 & data[0]) >> 4) + (((0x08 & data[0]) >> 3) * 0.5) + (((0x04 & data[0]) >> 2) * 0.25) + (((0x02 & data[0]) >> 1) * 0.125) + (((0x01 & data[0])) * 0.0625)
            if (0x08 & data[1]) == 0x08:
                temp = -temp
        return {'temperature': temp}

    def _read_DS2438(self, deviceId, enableWireLeveling=False):
        """
        Reads the value from a DS2438 device connected to a HIH-4021 family device on the 1-Wire bus.
        
        deviceId:
            The device id of the device to read. Must have been enumerated.
        
        enableWireLeveling:
            Enables the reader to use wire leveling to read from certain devices. Not used for DS2438.
        """
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
            data = [TMTouchByte(self._handle, 0xFF) for i in range(9)]
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
