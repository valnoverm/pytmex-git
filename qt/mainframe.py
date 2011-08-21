# -*- coding: utf-8 -*-
# Copyright (c) 2011 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

import sys
import time, datetime
import multiprocessing
import csv

from PyQt4 import QtGui
from PyQt4 import QtCore

from worker import oneWireWorker, Command, Result
from tmex import TMEXException

class MainFrame(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('1-Wire Network')
        
        (self.workerChannelLocal, workerChannelRemote) = multiprocessing.Pipe(True)
        self.worker = multiprocessing.Process(target=oneWireWorker, args=([workerChannelRemote]))
        self.worker.start()

        # Initialize members
        self.updateTimer = None
        self.workerTimer = self.startTimer(100)

        self.initializeWidgets()
        self.initializeMenus()
        
        self.enumerateDevices()
        self.startUpdatetimer(5000)

    def initializeWidgets(self):
        box = QtGui.QVBoxLayout()

        self.sourcesList = QtGui.QTreeWidget(self)
        self.sourcesList.setRootIsDecorated(False)
        self.sourcesList.setHeaderLabels(QtCore.QStringList([u"Id", u"Temperature", u"Humidity", u"Device", u"Description"]))
        self.sourcesList.setColumnWidth(0, 150)
        self.sourcesList.setColumnWidth(1, 75)
        self.sourcesList.setColumnWidth(2, 75)
        self.sourcesList.setColumnWidth(3, 50)

        box.addWidget(self.sourcesList, 1)
        
        formLayout = QtGui.QFormLayout()
        
        self.updateIntervalWidget = QtGui.QSpinBox()
        self.updateIntervalWidget.setMinimum(5)
        self.updateIntervalWidget.setMaximum(3600)
        
        formLayout.addRow(u"Update interval in seconds:", self.updateIntervalWidget)
        
        self.updateIntervalWidget.valueChanged.connect(self.updateUpdateInterval)
        
        box.addLayout(formLayout, 0)

        center = QtGui.QWidget()
        center.setLayout(box)
        self.setCentralWidget(center)

        # Set the status bar
        self.statusBar().showMessage('Ready')

        self.resize(800, 500)

    def initializeMenus(self):
        menuExit = QtGui.QAction('E&xit', self)
        menuExit.setShortcut('Ctrl+Q')
        menuExit.setStatusTip('Exit application')
        self.connect(menuExit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        menubar = self.menuBar()
        menuFile = menubar.addMenu('&File')
        menuFile.addAction(menuExit)

    def startUpdatetimer(self, timeout=100.0):
        if self.updateTimer:
            self.killTimer(self.updateTimer)
        self.updateTimer = self.startTimer(timeout)

    def closeEvent(self, event):
        if self.updateTimer:
            self.killTimer(self.updateTimer)
        self.workerChannelLocal.send(Command('exit', None))
        self.killTimer(self.workerTimer)

    def timerEvent(self, event):
        timerId = event.timerId()
        if (timerId == self.workerTimer):
            self.workerTimerEvent()
        if (timerId == self.updateTimer):
            self.updateTimerEvent()

    def updateTimerEvent(self):
        root = self.sourcesList.invisibleRootItem()
        for index in xrange(root.childCount()):
            item = root.child(index)
            if item.checkState(0) == QtCore.Qt.Checked:
                key = str(item.text(0))
                self.readDevice(key)

    def updateUpdateInterval(self, int):
        self.startUpdatetimer(int * 1000.0)

    def workerTimerEvent(self):
        while self.workerChannelLocal.poll():
            obj = self.workerChannelLocal.recv()
            if isinstance(obj, Result):
                root = self.sourcesList.invisibleRootItem()
                treeNode = None
                if obj.deviceId:
                    for index in xrange(root.childCount()):
                        node = root.child(index)
                        if node.text(0) == obj.deviceId:
                            treeNode = node
                            break
                if obj.command == 'enumerate':
                    if treeNode:
                        treeNode.setText(3, unicode(obj.result['name']))
                        treeNode.setText(4, unicode(obj.result['description']))
                    else:
                        node = QtGui.QTreeWidgetItem(root, QtCore.QStringList([obj.deviceId, u"", u"", obj.result['name'], obj.result['description']]))
                        node.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        node.setCheckState(0, QtCore.Qt.Checked)
                        root.addChild(node)
                        self.readDevice(obj.deviceId)
                elif obj.command == 'read' and treeNode:
                    dt = datetime.datetime.today()
                    dt = dt.replace(microsecond=0)
                    fields = [obj.deviceId, dt.isoformat(' '), "0", "0"]
                    if 'temperature' in obj.result:
                        treeNode.setText(1, u"%.2f °C" % obj.result['temperature'])
                        fields[2] = "%.2f" % (obj.result['temperature'])
                    if 'humidity' in obj.result:
                        treeNode.setText(2, u"%.0f %%" % obj.result['humidity'])
                        fields[3] = "%.2f" % (obj.result['humidity'])
                    with open('%s.csv' % (obj.deviceId), 'a') as f:
                        w = csv.writer(f)
                        w.writerow(fields)
            if isinstance(obj, TMEXException):
                print(obj)

    def enumerateDevices(self):
        self.workerChannelLocal.send(Command('enumerate', None))
    
    def readDevice(self, deviceId):
        self.workerChannelLocal.send(Command('read', deviceId))