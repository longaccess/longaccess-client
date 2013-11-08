#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
from PySide.QtCore import QUrl, QObject, Slot, Qt
from PySide.QtGui import QApplication, QFileDialog, QVBoxLayout, QWidget
from PySide.QtDeclarative import QDeclarativeView
import lacli.views.qrc_decrypt

class MainWindow(QDeclarativeView):
   
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Certificate entry")
        # QML resizes to main window
        self.setResizeMode(QDeclarativeView.SizeViewToRootObject)
	#Decrypt Create an URL to the QML file
	url = QUrl('qrc:/ui/KeyInput.qml')
	# Set the QML file and show
	self.setSource(url)

# Create Qt application and the QDeclarative view
app = QApplication(sys.argv)
import pdb; pdb.set_trace()
window = QWidget()
view = MainWindow()
layout = QVBoxLayout()
layout.addWidget(view)
window.setLayout(layout)
window.setWindowFlags(Qt.FramelessWindowHint)

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
