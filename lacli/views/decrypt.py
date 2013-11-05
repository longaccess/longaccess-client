#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
from PySide.QtCore import QUrl, QObject, Slot
from PySide.QtGui import QApplication, QFileDialog
from PySide.QtDeclarative import QDeclarativeView
import lacli.views.qrc_decrypt

# Create Qt application and the QDeclarative view
app = QApplication(sys.argv)
view = QDeclarativeView()
# Create an URL to the QML file
url = QUrl('qrc:/ui/cert.qml')
# Set the QML file and show
view.setSource(url)
view.setResizeMode(QDeclarativeView.SizeRootObjectToView)



class OutputSelector(QObject):
    def __init__(self):
        super(OutputSelector,self).__init__()

    @Slot(result=str)
    def getDirectory(self):
        return QFileDialog.getExistingDirectory(
            view, 'Select destination directory',
            view.rootObject().property('folder'))

    @Slot(str, result=bool)
    def dirExists(self, path):
        return os.path.isdir(path)

view.rootContext().setContextProperty("destsel", OutputSelector())
