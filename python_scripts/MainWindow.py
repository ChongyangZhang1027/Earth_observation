# add something
# add something
import os.path

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QTextEdit, QTextBrowser, QWidget, QHBoxLayout, QVBoxLayout, QMenuBar, QMainWindow,
                             QStatusBar)
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

import mapPlot


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.browser = None
        self.menuBar = None
        self.textBrowser = None
        self.setWindowTitle('Ocean energy helper')
        self.setGeometry(100, 100, 1500, 900)
        self._setStatusBar()
        self._setMapView()
        self._setLayout()
        self._setMenuBar()

    def _openMenu(self):
        self.statusBar.showMessage("Open")

    def _quitMenu(self):
        self.statusBar.showMessage("Quit")

    def _saveMenu(self):
        self.statusBar.showMessage("Save")

    def _setAreaMenu(self):
        self.statusBar.showMessage("Set area")

    def _defaultAreaMenu(self):
        self.statusBar.showMessage("Default area")

    def _processMenu(self):
        self.statusBar.showMessage("Process")

    def _setStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def _setMenuBar(self):
        self.menuBar = QMenuBar()
        fileMenu = self.menuBar.addMenu("File")
        editMenu = self.menuBar.addMenu("Edit")
        toolMenu = self.menuBar.addMenu("Tool")
        fileMenu.addAction("Open", self._openMenu)
        fileMenu.addAction("Save", self._saveMenu)
        fileMenu.addAction("Quit", self._quitMenu)
        editMenu.addAction("Set area", self._setAreaMenu)
        editMenu.addAction("Default area", self._defaultAreaMenu)
        toolMenu.addAction("Process", self._processMenu)
        self.setMenuBar(self.menuBar)

    def _setMapView(self):
        mapPlot.map_init()
        self.browser = QWebEngineView()
        currPath = os.path.dirname(__file__).replace("\\", "/")
        self.url = QtCore.QUrl(currPath + "/fareo_map.html")
        self.browser.load(self.url)

    def _setLayout(self):

        dynamic_canvas1 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        dynamic_canvas2 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        dynamic_canvas3 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        # self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(dynamic_canvas, self))
        self._dynamic_ax1 = dynamic_canvas1.figure.subplots()
        self._dynamic_ax2 = dynamic_canvas2.figure.subplots()
        self._dynamic_ax3 = dynamic_canvas3.figure.subplots()
        self._dynamic_ax1.set_title("Data view")
        self._dynamic_ax2.set_title("Ocean energy distribution map")
        self._dynamic_ax3.set_title("Ocean energy time series")
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setLineWrapMode(QTextEdit.NoWrap)
        self.textBrowser2 = QTextBrowser(self)
        self.textBrowser2.setLineWrapMode(QTextEdit.NoWrap)
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.browser)
        vbox1.addWidget(dynamic_canvas1)
        vbox1.setStretch(0, 1)
        vbox1.setStretch(1, 1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(dynamic_canvas2)
        vbox2.addWidget(dynamic_canvas3)
        vbox2.setStretch(0, 3)
        vbox2.setStretch(1, 1)

        vbox3 = QVBoxLayout()
        vbox3.addWidget(self.textBrowser)
        vbox3.addWidget(self.textBrowser2)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        hbox.addLayout(vbox3)
        hbox.setStretch(0, 2)
        hbox.setStretch(1, 3)
        hbox.setStretch(2, 1)

        centralWidget = QWidget()
        centralWidget.setLayout(hbox)
        self.setCentralWidget(centralWidget)

