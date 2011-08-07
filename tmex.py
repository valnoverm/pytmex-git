import ctypes

dll = ctypes.windll.LoadLibrary("IBFS64.DLL")

PortTypes = {
    1: "Older DS9097E-type serial port adapter",
    2: "Parallel port adapter",
    5: "Standard DS90907U-type serial port adapter",
    6: "USB port adapter",
}

SetupMessages = {
    0: "Setup failed",
    1: "Setup succeeded",
    2: "Setup ok but 1-Wire network shorted",
    3: "1-Wire network does not exist",
    4: "TMSetup not supported",
}

TMReadDefaultPort = dll.TMReadDefaultPort
TMReadDefaultPort.argtypes = [ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]
TMReadDefaultPort.restype = ctypes.c_short

TMExtendedStartSession = dll.TMExtendedStartSession
TMExtendedStartSession.argtypes = [ctypes.c_short, ctypes.c_short, ctypes.c_void_p]
TMExtendedStartSession.restype = ctypes.c_long

TMValidSession = dll.TMValidSession
TMValidSession.argtypes = [ctypes.c_long]
TMValidSession.restype = ctypes.c_short

TMEndSession = dll.TMEndSession
TMEndSession.argtypes = [ctypes.c_long]
TMEndSession.restype = ctypes.c_short

TMSetup = dll.TMSetup
TMSetup.argtypes = [ctypes.c_long]
TMSetup.restype = ctypes.c_short

TMFirst = dll.TMFirst
TMFirst.argtypes = [ctypes.c_long, ctypes.c_char_p]
TMFirst.restype = ctypes.c_short

TMNext = dll.TMNext
TMNext.argtypes = [ctypes.c_long, ctypes.c_char_p]
TMNext.restype = ctypes.c_short

TMRom = dll.TMRom
TMRom.argtypes = [ctypes.c_long, ctypes.c_char_p, ctypes.POINTER(ctypes.c_short)]
TMRom.restype = ctypes.c_short

TMCRC = dll.TMCRC
TMCRC.argtypes = [ctypes.c_short, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_ushort, ctypes.c_short]
TMCRC.restype = ctypes.c_short

class TMFamilySpec(ctypes.Structure):
    _fields_ = [("features", ctypes.c_ushort * 32), ("description", ctypes.c_char * 255)]

TMGetFamilySpec = dll.TMGetFamilySpec
TMGetFamilySpec.argtypes = [ctypes.c_long, ctypes.c_char_p, ctypes.POINTER(TMFamilySpec)]
TMGetFamilySpec.restype = ctypes.c_short

TMTouchReset = dll.TMTouchReset
TMTouchReset.argtypes = [ctypes.c_long]
TMTouchReset.restype = ctypes.c_short

TMAccess = dll.TMAccess
TMAccess.argtypes = [ctypes.c_long, ctypes.c_char_p]
TMAccess.restype = ctypes.c_short

TMTouchByte = dll.TMTouchByte
TMTouchByte.argtypes = [ctypes.c_long, ctypes.c_short]
TMTouchByte.restype = ctypes.c_short

TMOneWireLevel = dll.TMOneWireLevel
TMOneWireLevel.argtypes = [ctypes.c_long, ctypes.c_short, ctypes.c_short, ctypes.c_short]
TMOneWireLevel.restype = ctypes.c_short
