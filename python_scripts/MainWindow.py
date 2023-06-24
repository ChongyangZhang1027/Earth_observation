import math
import os.path
import time
from os import popen

import folium
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QTextEdit, QTextBrowser, QWidget, QHBoxLayout, QVBoxLayout, QMenuBar, QMainWindow,
                             QStatusBar, QFileDialog, QLineEdit, QLabel, QPushButton, QRadioButton, QFrame,
                             QButtonGroup, QMessageBox, QComboBox)
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas)
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolBar
from matplotlib.figure import Figure
import json
import numpy as np
# import datetime

import mapPlot
from algorithm import *
from ProcessThread import processThread


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.browser = None
        self.menuBar = None
        self.textBrowser = None
        self.map = None
        self.workspacePath = ""
        self.userName = ""
        self.passwd = ""
        self.monthIdxOfResult = 0
        self.boundary = []
        self.timeRange = [[], []]
        self.pThread = processThread()
        self.pThread.signal.connect(self._callback)
        self.filenames = [[], []]
        self.variables = ['VTM02', 'VSDX', 'VSDY', 'VHM0', 'zos']
        self.setWindowTitle('Ocean energy helper')
        self.setGeometry(100, 100, 1500, 900)
        self._setStatusBar()
        self._setMapView()
        self._setLayout()
        self._setMenuBar()
        self.browser.page().profile().downloadRequested.connect(
            self._handleDownloadRequest)

    def _handleDownloadRequest(self, item):
        path = "boundary.geojson"
        item.setPath(path)
        item.accept()

    def _strAddZero(self, timeStr):
        if len(timeStr) < 2:
            timeStr = '0' + timeStr
        return timeStr

    def _openMenu(self):
        self.workspacePath = QFileDialog.getExistingDirectory(
            self, 'set data folder', '')
        self.textBrowser2.append("workspace path: " + self.workspacePath + '\n')
        self.statusBar.showMessage("Open")

    def _quitMenu(self):
        self.statusBar.showMessage("Quit")

    def _saveMenu(self):
        self.statusBar.showMessage("Save")

    def _checkArea(self):
        if not self.boundary or len(self.boundary) != 4:
            self._alertMsg(3, "Set boundary!")
            return False
        if self.boundary[0][0] > MAX_LAT or self.boundary[2][0] < MIN_LAT or \
                self.boundary[0][1] < MIN_LON or self.boundary[1][1] > MAX_LON:
            self._alertMsg(3, "Boundary invalid!")
            return False

        dx = (self.boundary[0][0] - self.boundary[2][0]) / 180 * math.pi * EARTH_RADIUS / 1e3
        dy = (self.boundary[1][1] - self.boundary[0][1]) / 180 * math.pi * EARTH_RADIUS * \
             math.cos(self.boundary[0][0] / 180 * math.pi) / 1e3
        area = dx * dy
        if area > AREA_LIMIT:
            self._alertMsg(3, "Area too large!")
        return True

    def _checkTime(self, start, end, middle):
        if not start or not end:
            self._alertMsg(2, "Check time input!")
            return False
        startLimit = datetime.date(PRODUCT_START_YEAR, PRODUCT_START_MONTH, 1)
        endLimit = datetime.date(today.year, today.month, 1)
        startDate = datetime.date(start[0], start[1], start[2])
        endDate = datetime.date(end[0], end[1], end[2])
        if startDate < startLimit or endDate > endLimit or startDate >= endDate:
            self._alertMsg(2, "Time exceeds limit!")
            return False
        if not middle == []:
            middleDate = datetime.date(middle[0], middle[1], middle[2])
            if middleDate < startDate or middleDate > endDate:
                self._alertMsg(2, "Time exceeds limit!")
                return False
        return True

    def _download(self):
        if not self._checkArea():
            return
        if not self.timeRange:
            self._alertMsg(2, "Check time input!")
            return
        if not self._checkTime(self.timeRange[0], self.timeRange[1], []):
            return
        monthCnt = (self.timeRange[1][0] - self.timeRange[0][0]) * 12 + self.timeRange[1][1] - self.timeRange[0][1]
        self.workspacePath = "./workspace/"
        self.userName = "czhang17"
        self.passwd = "410302xyzZCY!"
        dataPath = self.workspacePath + "/data/"
        for monIdx in range(monthCnt):
            year = self.timeRange[0][0] + int(monIdx / 12)
            nextYear = self.timeRange[0][0] + int((monIdx + 1) / 12)
            currMon = (self.timeRange[0][1] + monIdx) % 12
            nextMon = (currMon + 1) % 12
            if currMon == 0:
                currMon = 12
            currMon = self._strAddZero(str(currMon))
            if nextMon == 0:
                nextMon = 12
            nextMon = self._strAddZero(str(nextMon))
            cmdLine = "python -m motuclient --motu https://nrt.cmems-du.eu/motu-web/Motu --service-id " \
                      "NORTHWESTSHELF_ANALYSIS_FORECAST_WAV_004_014-TDS --product-id MetO-NWS-WAV-hi" \
                      + " --longitude-min " + str(self.boundary[0][1]) + " --longitude-max " + str(self.boundary[1][1])\
                      + " --latitude-min " + str(self.boundary[2][0]) + " --latitude-max " + str(self.boundary[0][0]) \
                      + " --date-min \"" + str(year) + "-" + currMon + "-01 00:00:00\"" \
                        " --date-max \"" + str(nextYear) + "-" + str(nextMon) + "-01 00:00:00\"" \
                        " --variable VHM0 --variable VSDX --variable VSDY --variable VTM02" \
                        " --out-dir " + dataPath + " --out-name MetO-NWS-WAV-" + str(year) + "-" + str(currMon) + ".nc"\
                        " --user " + self.userName + " --pwd " + self.passwd
            self.textBrowser2.append("Downloading " + str(year) + "-" + currMon)
            downMsg = popen(cmdLine).read()
            self.textBrowser2.append(downMsg)
            cmdLine = "python -m motuclient --motu https://nrt.cmems-du.eu/motu-web/Motu --service-id " \
                      "NORTHWESTSHELF_ANALYSIS_FORECAST_PHY_004_013-TDS --product-id MetO-NWS-PHY-hi-SSH" \
                      + " --longitude-min " + str(self.boundary[0][1]) + " --longitude-max " + str(self.boundary[1][1])\
                      + " --latitude-min " + str(self.boundary[2][0]) + " --latitude-max " + str(self.boundary[0][0]) \
                      + " --date-min \"" + str(year) + "-" + currMon + "-01 00:00:00\"" \
                        " --date-max \"" + str(nextYear) + "-" + str(nextMon) + "-01 00:00:00\"" \
                      " --variable zos" \
                        " --out-dir " + dataPath + " --out-name MetO-NWS-PHY-hi-SSH-" + str(year) + "-" + str(currMon) + ".nc"\
                        " --user " + self.userName + " --pwd " + self.passwd
            self.textBrowser2.append("Downloading " + str(year) + "-" + currMon)
            downMsg = popen(cmdLine).read()
            self.textBrowser2.append(downMsg)
            self.textBrowser2.append(str(year) + "-" + currMon + "download finished")
            self.textBrowser2.append("\n")
            # print(cmdLine)

    def _setAreaMenu(self):
        boundary_json = open("boundary.geojson", "rb")
        jsonObj = json.load(boundary_json)
        boundary_json.close()
        points = jsonObj["features"][0]["geometry"]["coordinates"][0]
        self.boundary = [[points[1][1], points[1][0]], [points[2][1], points[2][0]],
                         [points[3][1], points[3][0]], [points[0][1], points[0][0]]]
        if not self._checkArea():
            self.boundary = []
            return
        self.textBrowser2.append('Set boundary successfully:')
        for pos in self.boundary:
            self.textBrowser2.append('(' + str(pos[0]) + ',' + str(pos[1]) + ')')
        self.textBrowser2.append("\n")
        self.statusBar.showMessage("Set area")

    def _defaultAreaMenu(self):
        self.boundary = [[62.75, -8], [62.75, -6], [61, -6], [61, -8]]
        self.textBrowser2.append('Set boundary successfully:')
        for pos in self.boundary:
            self.textBrowser2.append('(' + str(pos[0]) + ',' + str(pos[1]) + ')')
        self.textBrowser2.append("")
        folium.Rectangle([(62.75, -8), (61, -6)]).add_to(self.map)
        self.map.save("fareo_map.html")
        self.browser.load(self.url)
        self.statusBar.showMessage("Default area")

    def _setTimeRange(self):
        if self.inputBeginYear.text() == "" or self.inputBeginMonth.text() == "" or \
                self.inputEndYear.text() == "" or self.inputEndMonth.text() == "":
            self._alertMsg(2, "Check time input!")
            return
        self.timeRange = [[], []]

        self.timeRange[0] = [int(self.inputBeginYear.text()), int(self.inputBeginMonth.text()), 1, 0, 0, 0]
        self.timeRange[1] = [int(self.inputEndYear.text()), int(self.inputEndMonth.text()), 1, 0, 0, 0]
        if not self._checkTime(self.timeRange[0], self.timeRange[1], []):
            self.timeRange = [[], []]
            return
        self.textBrowser2.append("Set time range successfully")
        self.textBrowser2.append("Begin time: " + self.inputBeginYear.text() + "-" +
                                 self._strAddZero(self.inputBeginMonth.text()) + "-01 00:00:00")
        self.textBrowser2.append("End time:   " + self.inputEndYear.text() + "-" +
                                 self._strAddZero(self.inputEndMonth.text()) + "-01 00:00:00\n")
        self.statusBar.showMessage("set time range")

    def _defaultTime(self):
        self.timeRange = [[2022, 1, 1, 0, 0, 0], [2022, 4, 1, 0, 0, 0]]
        self.inputBeginYear.setText("2022")
        self.inputBeginMonth.setText("01")
        self.inputEndYear.setText("2022")
        self.inputEndMonth.setText("04")
        self.textBrowser2.append('Set time successfully:')
        self.textBrowser2.append("Begin time: 2022-01-01 00:00:00")
        self.textBrowser2.append("End time:   2022-04-01 00:00:00\n")
        self.statusBar.showMessage("Default time")

    def _clearAll(self):
        self.map = mapPlot.map_init()
        self.browser.load(self.url)
        self.boundary = []

    def _processMenu(self):
        # self._dataVisualization()
        # self._plotResult()
        if not self._checkArea():
            return
        if not self._checkTime(self.timeRange[0], self.timeRange[1], []):
            return
        if not self._checkData(True):
            return
        self.pThread.filenames = self.filenames
        time.sleep(1)
        self.pThread.start()

        self.statusBar.showMessage("Process")

    def _callback(self, energyList):
        self.oceanEnergy = energyList
        # print
        self.textBrowser.append('current power plant: [' + str(self.oceanEnergy[0].optSite[1][1]) + ', ' +
                                str(self.oceanEnergy[0].optSite[1][0]) + ']')
        self.textBrowser.append('average current power: ' + str(np.average(self.oceanEnergy[0].timeSeries)) +
                                ' W/m^2\n')

        self.textBrowser.append('wave potential power plant: [' + str(self.oceanEnergy[1].optSite[1][1]) + ', ' +
                                str(self.oceanEnergy[1].optSite[1][0]) + ']')
        self.textBrowser.append('average wave power: ' + str(np.average(self.oceanEnergy[1].timeSeries) / 1000) +
                                ' kW/m\n')

        self.textBrowser.append('tidal potential power plant: [' + str(self.oceanEnergy[2].optSite[1][1]) + ', ' +
                                str(self.oceanEnergy[2].optSite[1][0]) + ']')
        self.textBrowser.append('average tidal power: ' + str(np.average(self.oceanEnergy[2].timeSeries)) + ' W/m^2\n')

        self._plotResult(2, -1)

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
        fileMenu.addAction("Download", self._download)
        editMenu.addAction("Set area", self._setAreaMenu)
        editMenu.addAction("Default area", self._defaultAreaMenu)
        editMenu.addAction("Set time", self._setTimeRange)
        editMenu.addAction("Default time", self._defaultTime)
        editMenu.addAction("Clear", self._clearAll)
        toolMenu.addAction("Process", self._processMenu)
        self.setMenuBar(self.menuBar)

    def _setMapView(self):
        self.map = mapPlot.map_init()
        self.browser = QWebEngineView()
        currPath = os.path.dirname(__file__).replace("\\", "/")
        self.url = QtCore.QUrl(currPath + "/fareo_map.html")
        self.browser.load(self.url)

    def _setText(self):
        # begin time and end time
        self.inputBeginYear = QLineEdit(self)
        self.inputBeginYear.setValidator(QIntValidator(PRODUCT_START_YEAR, PRODUCT_END_YEAR, self))
        self.inputBeginMonth = QLineEdit(self)
        self.inputBeginMonth.setValidator(QIntValidator(1, 12, self))
        # self.inputBeginDay = QLineEdit(self)
        # self.inputBeginDay.setValidator(QIntValidator(1, 31, self))
        # self.inputBeginHour = QLineEdit(self)
        # self.inputBeginHour.setValidator(QIntValidator(0, 23, self))
        self.inputEndYear = QLineEdit(self)
        self.inputEndYear.setValidator(QIntValidator(PRODUCT_START_YEAR, PRODUCT_END_YEAR, self))
        self.inputEndMonth = QLineEdit(self)
        self.inputEndMonth.setValidator(QIntValidator(1, 12, self))
        # self.inputEndDay = QLineEdit(self)
        # self.inputEndDay.setValidator(QIntValidator(1, 31, self))
        # self.inputEndHour = QLineEdit(self)
        # self.inputEndHour.setValidator(QIntValidator(0, 23, self))

        # raw data show time
        self.rawDataYear = QLineEdit(self)
        self.rawDataYear.setValidator(QIntValidator(PRODUCT_START_YEAR, PRODUCT_END_YEAR, self))
        self.rawDataMonth = QLineEdit(self)
        self.rawDataMonth.setValidator(QIntValidator(1, 12, self))
        self.rawDataDay = QLineEdit(self)
        self.rawDataDay.setValidator(QIntValidator(1, 31, self))
        self.rawDataHour = QLineEdit(self)
        self.rawDataHour.setValidator(QIntValidator(0, 23, self))
        # self.rawDataType = QLineEdit(self)

        # result show time
        # self.resYear = QLineEdit(self)
        # self.resYear.setValidator(QIntValidator(PRODUCT_START_YEAR, PRODUCT_END_YEAR, self))
        # self.resMonth = QLineEdit(self)
        # self.resMonth.setValidator(QIntValidator(1, 12, self))
        # self.resDay = QLineEdit(self)
        # self.resDay.setValidator(QIntValidator(1, 31, self))
        # self.resHour = QLineEdit(self)
        # self.resHour.setValidator(QIntValidator(0, 23, self))
        # self.resType = QLineEdit(self)

        # message and summary
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setLineWrapMode(QTextEdit.NoWrap)
        self.textBrowser2 = QTextBrowser(self)
        self.textBrowser2.setLineWrapMode(QTextEdit.NoWrap)

    def _setCanvas(self):
        self.dynamic_canvas1 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        self.dynamic_canvas2 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        self.dynamic_canvas3 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        # self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(dynamic_canvas, self))
        self._dynamic_ax1 = self.dynamic_canvas1.figure.subplots()
        self._dynamic_ax2 = self.dynamic_canvas2.figure.subplots()
        self._dynamic_ax3 = self.dynamic_canvas3.figure.subplots()
        self._dynamic_ax1.set_title("Data view")
        self._dynamic_ax2.set_title("Ocean energy distribution map")
        self._dynamic_ax3.set_title("Ocean energy time series")
        self.figToolBar1 = NavigationToolBar(self.dynamic_canvas1, self)
        self.figToolBar2 = NavigationToolBar(self.dynamic_canvas2, self)
        self.figToolBar3 = NavigationToolBar(self.dynamic_canvas3, self)
        self.rawDataColorBar = ''
        self.resultColorBar = ''

    def _setLayout(self):
        self.centralWidget = QWidget()
        # left column of the layout, map and raw data view
        self._setCanvas()
        self._setText()
        hboxInputTimeCtrl = QHBoxLayout()
        hboxInputTimeCtrl.addWidget(QLabel('Begin: '))
        hboxInputTimeCtrl.addWidget(QLabel('year'))
        hboxInputTimeCtrl.addWidget(self.inputBeginYear)
        hboxInputTimeCtrl.addWidget(QLabel('month'))
        hboxInputTimeCtrl.addWidget(self.inputBeginMonth)

        hboxInputTimeCtrl.addWidget(QLabel('  End: '))
        hboxInputTimeCtrl.addWidget(QLabel('year'))
        hboxInputTimeCtrl.addWidget(self.inputEndYear)
        hboxInputTimeCtrl.addWidget(QLabel('month'))
        hboxInputTimeCtrl.addWidget(self.inputEndMonth)
        # hboxInputBeginCtrl.addWidget(QLabel('day'))
        # hboxInputBeginCtrl.addWidget(self.inputBeginDay)
        # hboxInputBeginCtrl.addWidget(QLabel('hour'))
        # hboxInputBeginCtrl.addWidget(self.inputBeginHour)

        # hboxInputEndCtrl = QHBoxLayout()
        # hboxInputEndCtrl.addWidget(QLabel('day'))
        # hboxInputEndCtrl.addWidget(self.inputEndDay)
        # hboxInputEndCtrl.addWidget(QLabel('hour'))
        # hboxInputEndCtrl.addWidget(self.inputEndHour)

        self.rawDataShowBtn = QPushButton(self)
        self.rawDataShowBtn.setText('show')
        self.rawDataShowBtn.clicked.connect(self._dataVisualization)

        self.comBox = QComboBox(self)
        self.comBox.addItems(['VTM02', 'VSDX', 'VSDY', 'VHM0', 'zos'])

        hboxRawDataCtrl = QHBoxLayout()
        # hboxRawDataCtrl.addWidget(QLabel('param'))
        hboxRawDataCtrl.addWidget(self.comBox)
        # hboxRawDataCtrl.addWidget(self.rawDataType)
        hboxRawDataCtrl.addWidget(QLabel('year'))
        hboxRawDataCtrl.addWidget(self.rawDataYear)
        hboxRawDataCtrl.addWidget(QLabel('month'))
        hboxRawDataCtrl.addWidget(self.rawDataMonth)
        hboxRawDataCtrl.addWidget(QLabel('day'))
        hboxRawDataCtrl.addWidget(self.rawDataDay)
        hboxRawDataCtrl.addWidget(QLabel('hour'))
        hboxRawDataCtrl.addWidget(self.rawDataHour)
        hboxRawDataCtrl.addWidget(self.rawDataShowBtn)
        vbox1 = QVBoxLayout()

        vbox1.addLayout(hboxInputTimeCtrl)
        # vbox1.addLayout(hboxInputEndCtrl)
        vbox1.addWidget(self.browser)
        vbox1.addLayout(hboxRawDataCtrl)
        vbox1.addWidget(self.dynamic_canvas1)
        vbox1.addWidget(self.figToolBar1)
        vbox1.setStretch(1, 1)
        vbox1.setStretch(3, 1)

        # middle column of the layout, result on map, and time series
        self.resPrevBtn = QPushButton(self)
        self.resPrevBtn.setText('prev')
        self.resPrevBtn.clicked.connect(self._setPrevEpoch)
        self.resNextBtn = QPushButton(self)
        self.resNextBtn.setText('next')
        self.resNextBtn.clicked.connect(self._setNextEpoch)

        # self.resShowMonthBtn = QRadioButton('Monthly')
        # self.resShowMonthBtn.setChecked(True)
        # self.resShowMonthBtn.toggled.connect(self._setTimeResolution)
        # self.resShowDayBtn = QRadioButton('Daily  ')
        # self.resShowDayBtn.toggled.connect(self._setTimeResolution)
        # self.resShowHourBtn = QRadioButton('Hourly ')
        # self.resShowHourBtn.toggled.connect(self._setTimeResolution)
        # timeBtnGrp = QButtonGroup(self.centralWidget)
        # timeBtnGrp.addButton(self.resShowMonthBtn)
        # timeBtnGrp.addButton(self.resShowDayBtn)
        # timeBtnGrp.addButton(self.resShowHourBtn)

        self.resTypeBtn1 = QRadioButton('Tidal energy')
        self.resTypeBtn1.setChecked(True)
        self.resTypeBtn1.toggled.connect(self._setResType)
        self.resTypeBtn2 = QRadioButton('Wave potential')
        self.resTypeBtn2.toggled.connect(self._setResType)
        self.resTypeBtn3 = QRadioButton('Current energy')
        self.resTypeBtn3.toggled.connect(self._setResType)
        typeBtnGrp = QButtonGroup(self.centralWidget)
        typeBtnGrp.addButton(self.resTypeBtn1)
        typeBtnGrp.addButton(self.resTypeBtn2)
        typeBtnGrp.addButton(self.resTypeBtn3)

        hboxResShowBtn1 = QHBoxLayout()
        # hboxResShowBtn.addWidget(QLabel('type'))
        # hboxResShowBtn.addWidget(self.resType)
        # hboxResShowBtn1.addWidget(QLabel('year '))
        # hboxResShowBtn1.addWidget(self.resYear)
        # hboxResShowBtn1.addWidget(QLabel('month'))
        # hboxResShowBtn1.addWidget(self.resMonth)
        # hboxResShowBtn1.addWidget(self.resShowMonthBtn)
        # hboxResShowBtn1.addWidget(self.resShowDayBtn)
        # hboxResShowBtn1.addWidget(self.resShowHourBtn)
        # hboxResShowBtn1.addWidget(self.resPrevBtn)

        hboxResShowBtn2 = QHBoxLayout()
        # hboxResShowBtn2.addWidget(QLabel('day  '))
        # hboxResShowBtn2.addWidget(self.resDay)
        # hboxResShowBtn2.addWidget(QLabel('hour '))
        # hboxResShowBtn2.addWidget(self.resHour)
        hboxResShowBtn2.addWidget(self.resTypeBtn1)
        hboxResShowBtn2.addWidget(self.resTypeBtn2)
        hboxResShowBtn2.addWidget(self.resTypeBtn3)
        hboxResShowBtn2.addWidget(self.resPrevBtn)
        hboxResShowBtn2.addWidget(self.resNextBtn)

        vbox2 = QVBoxLayout()
        # vbox2.addLayout(hboxResShowBtn1)
        vbox2.addLayout(hboxResShowBtn2)
        vbox2.addWidget(self.dynamic_canvas2)
        vbox2.addWidget(self.figToolBar2)
        vbox2.addWidget(self.dynamic_canvas3)
        vbox2.addWidget(self.figToolBar3)
        vbox2.setStretch(1, 3)
        vbox2.setStretch(2, 1)

        # right column of the layout, upper and lower part, to show different text result
        vbox3 = QVBoxLayout()
        vbox3.addWidget(self.textBrowser)
        vbox3.addWidget(self.textBrowser2)

        vLine = QFrame()
        vLine.setFrameShape(QFrame.VLine)
        vLine2 = QFrame()
        vLine2.setFrameShape(QFrame.VLine)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addWidget(vLine)
        hbox.addLayout(vbox2)
        hbox.addWidget(vLine2)
        hbox.addLayout(vbox3)
        hbox.setStretch(0, 2)
        hbox.setStretch(2, 3)
        hbox.setStretch(4, 1)

        # the QMainWindow inherit the QWidget, but it can not directly set layout, use the center widget of the window
        self.centralWidget.setLayout(hbox)
        self.setCentralWidget(self.centralWidget)

    def _setTimeResolution(self):
        a = 0

    def _setNextEpoch(self):
        if self.monthIdxOfResult + 1 >= len(self.oceanEnergy[0].monPowerMap):
            self._alertMsg(5, 'No next epoch!')
            return
        self.monthIdxOfResult = self.monthIdxOfResult + 1
        self._plotResult(2, self.monthIdxOfResult)

    def _setPrevEpoch(self):
        if self.monthIdxOfResult - 1 < -1:
            self._alertMsg(5, 'No previous epoch!')
            return
        self.monthIdxOfResult = self.monthIdxOfResult - 1
        self._plotResult(2, self.monthIdxOfResult)

    def _setResType(self):
        a = 0

    def _alertMsg(self, errorNum, errorMsg):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error type: " + str(errorNum))
        msg.setWindowTitle("Error")
        msg.setInformativeText(errorMsg)
        msg.exec_()

    def _checkData(self, showPath=True):
        if self.workspacePath == "":
            self._alertMsg(1, "Check workspace path!")
            return False
        dataPath = self.workspacePath + "/data/"
        if not os.path.exists(dataPath):
            self._alertMsg(1, "Check data path!")
            return False
        fileList = os.walk(dataPath)
        if showPath:
            self.textBrowser2.append("Files read:")
        wavFileCnt = 0
        sshFileCnt = 0
        self.filenames = [[], []]
        for root, dir, fileList in fileList:
            for file in fileList:
                if showPath:
                    self.textBrowser2.append(file)
                if not file.find("WAV") == -1:
                    wavFileCnt = wavFileCnt + 1
                    self.filenames[0].append(dataPath + file)
                if not file.find("SSH") == -1:
                    sshFileCnt = sshFileCnt + 1
                    self.filenames[1].append(dataPath + file)

        if showPath:
            self.textBrowser2.append("\n")
        if not fileList:
            self._alertMsg(1, "No data files!")
            self.filenames = [[], []]
            return False
        if not wavFileCnt == sshFileCnt:
            self._alertMsg(1, "Check data files!")
            self.filenames = [[], []]
            return False
        # print(self.filenames)
        return True

    def _dataVisualization(self):
        if not self._checkData(False):
            return

        param = self.comBox.currentText()
        year = self.rawDataYear.text()
        month = self.rawDataMonth.text()
        day = self.rawDataDay.text()
        hour = self.rawDataHour.text()

        if param == '' or year == '' or month == '' or day == '' or hour == '':
            self._alertMsg(2, "Check time input!")
            return

        if not self._checkTime(self.timeRange[0], self.timeRange[1], [int(year), int(month), 15, 0, 0, 0]):
            return

        month = self._strAddZero(month)
        day = self._strAddZero(day)
        hour = self._strAddZero(hour)

        latParamName = 'lat'
        lonParamName = 'lon'
        if param == "zos":
            fileList = self.filenames[1]
        else:
            fileList = self.filenames[0]
            latParamName = 'latitude'
            lonParamName = 'longitude'
        fp = ''
        fileExistFlag = False
        for file in fileList:
            if not file.find(year + '-' + month) == -1:
                fileExistFlag = True
                fp = file
                break
        if not fileExistFlag:
            self._alertMsg(1, "Check data file!")
            return
        data_set = xr.open_dataset(fp)
        time_stamp = year + "-" + str(month) + "-" + str(day) + "T" + str(hour) + ":00:00"
        data = data_set[param].sel(time=time_stamp, method="nearest")

        self._dynamic_ax1.clear()
        if not self.rawDataColorBar == '':
            self.rawDataColorBar.remove()
        lat = data_set[latParamName]
        lon = data_set[lonParamName]
        lon, lat = np.meshgrid(lon, lat)
        if param == 'VTM02':
            title = 'Spectral moments (0,2) wave period Tm02'
        elif param == 'VSDX':
            title = 'Stokes drift U'
        elif param == 'VSDY':
            title = 'Stokes drift V'
        elif param == 'VHM0':
            title = 'Spectral significant wave height (Hm0)'
        else:
            title = 'Sea surface height above geoid'
        self._dynamic_ax1.set_title(title)
        if param == 'zos':
            data = data[0]
        c = self._dynamic_ax1.pcolor(lon, lat, data[:, :])
        self._dynamic_ax1.set_xlabel('lon / deg')
        self._dynamic_ax1.set_ylabel('lat / deg')
        self._dynamic_ax1.axis('equal')
        self._dynamic_ax1.axis('tight')
        self.rawDataColorBar = self.dynamic_canvas1.figure.colorbar(c, ax=self._dynamic_ax1)
        # self.dynamic_canvas1.figure.colorbar(ax=self._dynamic_ax1)
        self._dynamic_ax1.figure.canvas.draw()

    def _plotResult(self, typeIdx, monthIdx):
        self._dynamic_ax2.clear()
        if not self.resultColorBar == '':
            self.resultColorBar.remove()
        self._dynamic_ax3.clear()
        if typeIdx == 0:
            title0 = 'Current energy distribution [W/m^2] '
            title2 = ' [W/m^2]'
            title = 'Current energy time series'
            yLabel = 'power [W/m^2]'
        elif typeIdx == 1:
            title0 = 'Wave energy distribution [kW/m] '
            title2 = ' [kW/m]'
            title = 'Wave energy time series'
            yLabel = 'power [kW/m]'
        elif typeIdx == 2:
            title0 = 'Tidal energy distribution '
            title2 = ' [W/m^2]'
            title = 'Tidal energy time series'
            yLabel = 'power [W/m^2]'
        else:
            self._alertMsg(4, 'Data type error!')
            return
        # plot time series
        self._dynamic_ax3.plot(self.oceanEnergy[typeIdx].timeIdx, self.oceanEnergy[typeIdx].timeSeries, marker='.')
        self._dynamic_ax3.set_title(title)
        self._dynamic_ax3.set_xlabel('time [day]')
        self._dynamic_ax3.set_ylabel(yLabel)
        self._dynamic_ax3.grid()
        self._dynamic_ax3.figure.canvas.draw()

        # plot distribution map
        lon, lat = np.meshgrid(self.oceanEnergy[typeIdx].lon, self.oceanEnergy[typeIdx].lat)
        if monthIdx == -1:
            c = self._dynamic_ax2.pcolor(lon, lat, self.oceanEnergy[typeIdx].totalPowerMap)
            title1 = 'average'
        else:
            c = self._dynamic_ax2.pcolor(lon, lat, self.oceanEnergy[typeIdx].monPowerMap[monthIdx])
            title1 = self.filenames[0][monthIdx][-10:-3]
        self._dynamic_ax2.set_title(title0 + title1 + title2)
        self._dynamic_ax2.set_xlabel('lon [deg]')
        self._dynamic_ax2.set_ylabel('lat [deg]')
        self.resultColorBar = self.dynamic_canvas2.figure.colorbar(c, ax=self._dynamic_ax2)
        self._dynamic_ax2.scatter(self.oceanEnergy[typeIdx].optSite[1][1], self.oceanEnergy[typeIdx].optSite[1][0],
                                  marker='^')
        self._dynamic_ax2.figure.canvas.draw()

        # # plot
        # lon, lat = np.meshgrid(lon, lat)
        # plt.figure()
        # plt.pcolor(lon, lat, currentEnergy.totalPowerMap)
        # plt.colorbar()
        # plt.scatter(currentEnergy.optSite[1][1], currentEnergy.optSite[1][0], marker='^')
        # plt.title('Current energy distribution map [W/m^2]')
        # plt.xlabel('lon [deg]')
        # plt.ylabel('lat [deg]')
       #
        # plt.figure()
        # plt.pcolor(lon, lat, wavePotential.totalPowerMap / 1000)
        # plt.colorbar()
        # plt.scatter(wavePotential.optSite[1][1], wavePotential.optSite[1][0], marker='^')
        # plt.title('Wave energy distribution map [kW/m]')
        # plt.xlabel('lon [deg]')
        # plt.ylabel('lat [deg]')
