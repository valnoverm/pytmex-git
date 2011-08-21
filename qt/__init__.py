# -*- coding: utf-8 -*-
# Copyright (c) 2011 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.

import sys
import mainframe
from PyQt4 import QtGui

def main():
    app = QtGui.QApplication(sys.argv)
    frame = mainframe.MainFrame()
    frame.show()
    frame.raise_() # Raise the window to the top (Only required on Mac OS X?)
    sys.exit(app.exec_())
