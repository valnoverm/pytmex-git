# -*- coding: utf-8 -*-
# Copyright (c) 2011 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

import ctypes, platform

# arch_bits should be either '32bit' or '64bit', arch_linker should be 'WindowsPE' on Windows.
(arch_bits, arch_linker) = platform.architecture() 
library = "IBFS64.DLL" if arch_bits == '64bit' else "IBFS32.DLL"

try:
    dll = ctypes.windll.LoadLibrary(library)
except:
    raise Exception("Library '{}' not found".format(library))

PortTypes = {
    1: "Older DS9097E-type serial port adapter",
    2: "Parallel port adapter",
    5: "Standard DS90907U-type serial port adapter",
    6: "USB port adapter",
}

TMReadDefaultPort = dll.TMReadDefaultPort
TMReadDefaultPort.argtypes = [ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]
TMReadDefaultPort.restype = ctypes.c_short
TMReadDefaultPortMessages = {
    1: "Succeeded",
    -2: "Defaults not found",
}

TMExtendedStartSession = dll.TMExtendedStartSession
TMExtendedStartSession.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_void_p]
TMExtendedStartSession.restype = ctypes.c_long
TMExtendedStartSessionMessages = {
    0: "Port not available",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMValidSession = dll.TMValidSession
TMValidSession.argtypes = [ctypes.c_long]
TMValidSession.restype = ctypes.c_short
TMValidSessionMessages = {
    0: "Session is invalid",
    1: "Session is valid",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMEndSession = dll.TMEndSession
TMEndSession.argtypes = [ctypes.c_long]
TMEndSession.restype = ctypes.c_short
TMEndSessionMessages = {
    0: "Session already invalid",
    1: "Session ended",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMSetup = dll.TMSetup
TMSetup.argtypes = [ctypes.c_long]
TMSetup.restype = ctypes.c_short
TMSetupMessages = {
    0: "Setup failed",
    1: "Setup succeeded",
    2: "Setup ok but 1-Wire network shorted",
    3: "1-Wire network does not exist",
    4: "TMSetup not supported",
    -1: "1-Wire network not initialized",
    -2: "1-Wire network does not exists",
    -3: "Function not supported",
    -12: "Failed to communicate with hardware adapter",
    -13: "An unsolicited event occurred on the 1-Wire",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMFirst = dll.TMFirst
TMFirst.argtypes = [ctypes.c_long, ctypes.c_char_p]
TMFirst.restype = ctypes.c_short
TMFirstMessages = {
    0: "Device not found",
    1: "Device found",
    -1: "1-Wire network not initialized",
    -2: "1-Wire network does not exists",
    -3: "Function not supported",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMNext = dll.TMNext
TMNext.argtypes = [ctypes.c_long, ctypes.c_char_p]
TMNext.restype = ctypes.c_short
TMNextMessages = {
    0: "Device not found",
    1: "Device found",
    -1: "1-Wire network not initialized",
    -2: "1-Wire network does not exists",
    -3: "Function not supported",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMRom = dll.TMRom
TMRom.argtypes = [ctypes.c_long, ctypes.c_char_p, ctypes.POINTER(ctypes.c_short)]
TMRom.restype = ctypes.c_short
TMRomMessages = {
    1: "Success",
    -1: "1-Wire network not initialized",
    -2: "1-Wire network does not exists",
    -3: "Function not supported",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMAccess = dll.TMAccess
TMAccess.argtypes = [ctypes.c_long, ctypes.c_char_p]
TMAccess.restype = ctypes.c_short
TMAccessMessages = {
    0: "Failed",
    1: "Success",
    -1: "1-Wire network not initialized",
    -2: "1-Wire network does not exists",
    -3: "Function not supported",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMCRC = dll.TMCRC
TMCRC.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_ushort, ctypes.c_short]
TMCRC.restype = ctypes.c_short
TMCRCMessages = {
    1: "Success",
    -1: "1-Wire network not initialized",
    -2: "1-Wire network does not exists",
    -3: "Function not supported",
    -4: "Error reading or writing package",
    -5: "Buffer is too small",
    -6: "Device is too small",
    -7: "No device found",
    -8: "Data block is too big",
    -9: "Wrong device for function",
    -10: "Page read is redirected",
    -11: "Programming not possible",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

class TMFamilySpec(ctypes.Structure):
    _fields_ = [("features", ctypes.c_ushort * 32), ("description", ctypes.c_char * 255)]

TMGetFamilySpec = dll.TMGetFamilySpec
TMGetFamilySpec.argtypes = [ctypes.c_long, ctypes.c_char_p, ctypes.POINTER(TMFamilySpec)]
TMGetFamilySpec.restype = ctypes.c_short

TMTouchReset = dll.TMTouchReset
TMTouchReset.argtypes = [ctypes.c_long]
TMTouchReset.restype = ctypes.c_short
TMTouchResetMessages = {
    0: "No presence pulse detected",
    1: "Precence pulse detected",
    2: "Alarming presence pulse detected",
    3: "1-Wire network shorted",
    5: "TMTouchReset not supported",
    -1: "1-Wire network not initialized",
    -2: "1-Wire network does not exists",
    -3: "Function not supported",
    -12: "Failed to communicate with hardware adapter",
    -13: "An unsolicited event occurred on the 1-Wire",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMTouchByte = dll.TMTouchByte
TMTouchByte.argtypes = [ctypes.c_long, ctypes.c_short]
TMTouchByte.restype = ctypes.c_short
TMTouchByteMessages = {
    255: "1-Wire network shorted",
    -1: "1-Wire network not initialized",
    -2: "1-Wire network does not exists",
    -3: "Function not supported",
    -12: "Failed to communicate with hardware adapter",
    -13: "An unsolicited event occurred on the 1-Wire",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

TMOneWireLevel = dll.TMOneWireLevel
TMOneWireLevel.argtypes = [ctypes.c_long, ctypes.c_short, ctypes.c_short, ctypes.c_short]
TMOneWireLevel.restype = ctypes.c_short
TMOneWireLevelMessages = {
    -1: "1-Wire network not initialized",
    -2: "1-Wire network does not exists",
    -3: "Function not supported",
    -12: "Failed to communicate with hardware adapter",
    -13: "An unsolicited event occurred on the 1-Wire",
    -200: "Session is invalid",
    -201: "Required hardware driver not found",
}

class TMEXException(Exception):
    pass
