#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtDeclarative import QDeclarativeView

# Create Qt application and the QDeclarative view
app = QApplication(sys.argv)
view = QDeclarativeView()
# Create an URL to the QML file
url = QUrl(':/cert.qml')
# Set the QML file and show
view.setSource(url)
view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
