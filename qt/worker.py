import time
import multiprocessing
from collections import namedtuple

from tmex import Session, TMEXException

Command = namedtuple('Command', ['command', 'deviceId'])
Result = namedtuple('Result', ['command', 'deviceId', 'result'])

def oneWireWorker(channel, port=0):
    run = True
    try:
        session = Session(port=port)
        devices = session.enumrate()
    except TMEXException, e:
        channel.send(e)
        run = False
    while run:
        if channel.poll():
            obj = channel.recv()
            if isinstance(obj, Command):
                if obj.command == 'exit':
                    run = False
                elif obj.command == 'enumerate':
                    try:
                        devices = session.enumrate()
                        for deviceId, information in devices.iteritems():
                            channel.send(Result('enumerate', deviceId, information))
                    except TMEXException, e:
                        channel.send(e)
                elif obj.command == 'read':
                    try:
                        readout = session.readDevice(obj.deviceId, enableWireLeveling=True)
                        channel.send(Result('read', obj.deviceId, readout))
                    except ValueError:
                        channel.send(TMEXException('Invalid id'))
                    except TMEXException, e:
                        channel.send(e)
        else:
            time.sleep(0.1)
    try:
        channel.send(Result('exit', None, None))
    except IOError:
        pass
