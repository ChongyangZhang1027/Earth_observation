import os.path

import folium
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QTextEdit, QTextBrowser, QWidget, QHBoxLayout, QVBoxLayout, QMenuBar, QMainWindow,
                             QStatusBar, QFileDialog, QLineEdit, QLabel, QPushButton, QRadioButton, QFrame,
                             QButtonGroup)
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas)
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolBar
from matplotlib.figure import Figure
# from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import json
import netCDF4
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

import mapPlot


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.browser = None
        self.menuBar = None
        self.textBrowser = None
        self.map = None
        self.boundary = []
        self.inputDataRange = [[2000, 1, 1, 0, 0, 0], [2023, 1, 1, 0, 0, 0]]
        self.setWindowTitle('Ocean energy helper')
        self.setGeometry(100, 100, 1500, 900)
        self._setStatusBar()
        self._setMapView()
        self._setLayout()
        self._setMenuBar()
        self.browser.page().profile().downloadRequested.connect(
            self._handleDownloadRequest)

    def _handleDownloadRequest(self, item):
        # path, _ = QFileDialog.getSaveFileName(
        #     self, "Save File", item.suggestedFileName()
        # )
        path = "boundary.geojson"
        item.setPath(path)
        item.accept()

    def _openMenu(self):
        self.statusBar.showMessage("Open")

    def _quitMenu(self):
        self.statusBar.showMessage("Quit")

    def _saveMenu(self):
        self.statusBar.showMessage("Save")

    def _setAreaMenu(self):
        boundary_json = open("boundary.geojson", "rb")
        jsonObj = json.load(boundary_json)
        boundary_json.close()
        points = jsonObj["features"][0]["geometry"]["coordinates"][0]
        self.boundary = [points[1], points[2], points[3], points[0]]
        print(self.boundary)
        self.statusBar.showMessage("Set area")

    def _defaultAreaMenu(self):
        self.boundary = [[-8.4, 62.8], [62.8, -5.4], [60, -5.4], [60, -8.4]]
        folium.Rectangle([(62.8, -8.4), (61, -5.4)]).add_to(self.map)
        self.map.save("fareo_map.html")
        self.browser.load(self.url)
        self.statusBar.showMessage("Default area")

    def _clearAll(self):
        self.map = mapPlot.map_init()
        self.browser.load(self.url)
        self.boundary = []

    def _processMenu(self):
        self._dataVisualization()
        self._plotResult()
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
        self.inputBeginYear.setValidator(QIntValidator(self.inputDataRange[0][0], self.inputDataRange[1][0], self))
        self.inputBeginMonth = QLineEdit(self)
        self.inputBeginMonth.setValidator(QIntValidator(1, 12, self))
        self.inputBeginDay = QLineEdit(self)
        self.inputBeginDay.setValidator(QIntValidator(1, 31, self))
        self.inputBeginHour = QLineEdit(self)
        self.inputBeginHour.setValidator(QIntValidator(0, 23, self))
        self.inputEndYear = QLineEdit(self)
        self.inputEndYear.setValidator(QIntValidator(self.inputDataRange[0][0], self.inputDataRange[1][0], self))
        self.inputEndMonth = QLineEdit(self)
        self.inputEndMonth.setValidator(QIntValidator(1, 12, self))
        self.inputEndDay = QLineEdit(self)
        self.inputEndDay.setValidator(QIntValidator(1, 31, self))
        self.inputEndHour = QLineEdit(self)
        self.inputEndHour.setValidator(QIntValidator(0, 23, self))

        # raw data show time
        self.rawDataYear = QLineEdit(self)
        self.rawDataYear.setValidator(QIntValidator(self.inputDataRange[0][0], self.inputDataRange[1][0], self))
        self.rawDataMonth = QLineEdit(self)
        self.rawDataMonth.setValidator(QIntValidator(1, 12, self))
        self.rawDataDay = QLineEdit(self)
        self.rawDataDay.setValidator(QIntValidator(1, 31, self))
        self.rawDataHour = QLineEdit(self)
        self.rawDataHour.setValidator(QIntValidator(0, 23, self))
        self.rawDataType = QLineEdit(self)

        # result show time
        self.resYear = QLineEdit(self)
        self.resYear.setValidator(QIntValidator(self.inputDataRange[0][0], self.inputDataRange[1][0], self))
        self.resMonth = QLineEdit(self)
        self.resMonth.setValidator(QIntValidator(1, 12, self))
        self.resDay = QLineEdit(self)
        self.resDay.setValidator(QIntValidator(1, 31, self))
        self.resHour = QLineEdit(self)
        self.resHour.setValidator(QIntValidator(0, 23, self))
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

    def _setLayout(self):
        self.centralWidget = QWidget()
        # left column of the layout, map and raw data view
        self._setCanvas()
        self._setText()
        hboxInputBeginCtrl = QHBoxLayout()
        hboxInputBeginCtrl.addWidget(QLabel('Begin: '))
        hboxInputBeginCtrl.addWidget(QLabel('year'))
        hboxInputBeginCtrl.addWidget(self.inputBeginYear)
        hboxInputBeginCtrl.addWidget(QLabel('month'))
        hboxInputBeginCtrl.addWidget(self.inputBeginMonth)
        hboxInputBeginCtrl.addWidget(QLabel('day'))
        hboxInputBeginCtrl.addWidget(self.inputBeginDay)
        hboxInputBeginCtrl.addWidget(QLabel('hour'))
        hboxInputBeginCtrl.addWidget(self.inputBeginHour)

        hboxInputEndCtrl = QHBoxLayout()
        hboxInputEndCtrl.addWidget(QLabel('End:   '))
        hboxInputEndCtrl.addWidget(QLabel('year'))
        hboxInputEndCtrl.addWidget(self.inputEndYear)
        hboxInputEndCtrl.addWidget(QLabel('month'))
        hboxInputEndCtrl.addWidget(self.inputEndMonth)
        hboxInputEndCtrl.addWidget(QLabel('day'))
        hboxInputEndCtrl.addWidget(self.inputEndDay)
        hboxInputEndCtrl.addWidget(QLabel('hour'))
        hboxInputEndCtrl.addWidget(self.inputEndHour)

        self.rawDataShowBtn = QPushButton(self)
        self.rawDataShowBtn.setText('show')
        self.rawDataShowBtn.clicked.connect(self._dataVisualization)

        hboxRawDataCtrl = QHBoxLayout()
        hboxRawDataCtrl.addWidget(QLabel('param'))
        hboxRawDataCtrl.addWidget(self.rawDataType)
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

        vbox1.addLayout(hboxInputBeginCtrl)
        vbox1.addLayout(hboxInputEndCtrl)
        vbox1.addWidget(self.browser)
        vbox1.addLayout(hboxRawDataCtrl)
        vbox1.addWidget(self.dynamic_canvas1)
        vbox1.addWidget(self.figToolBar1)
        vbox1.setStretch(2, 1)
        vbox1.setStretch(4, 1)

        # middle column of the layout, result on map, and time series
        self.resPrevBtn = QPushButton(self)
        self.resPrevBtn.setText('prev')
        self.resPrevBtn.clicked.connect(self._setPrevEpoch)
        self.resNextBtn = QPushButton(self)
        self.resNextBtn.setText('next')
        self.resNextBtn.clicked.connect(self._setNextEpoch)

        self.resShowMonthBtn = QRadioButton('Monthly')
        self.resShowMonthBtn.setChecked(True)
        self.resShowMonthBtn.toggled.connect(self._setTimeResolution)
        self.resShowDayBtn = QRadioButton('Daily  ')
        self.resShowDayBtn.toggled.connect(self._setTimeResolution)
        self.resShowHourBtn = QRadioButton('Hourly ')
        self.resShowHourBtn.toggled.connect(self._setTimeResolution)
        timeBtnGrp = QButtonGroup(self.centralWidget)
        timeBtnGrp.addButton(self.resShowMonthBtn)
        timeBtnGrp.addButton(self.resShowDayBtn)
        timeBtnGrp.addButton(self.resShowHourBtn)

        self.resTypeBtn1 = QRadioButton('Tidal  ')
        self.resTypeBtn1.setChecked(True)
        self.resTypeBtn1.toggled.connect(self._setResType)
        self.resTypeBtn2 = QRadioButton('Wave   ')
        self.resTypeBtn2.toggled.connect(self._setResType)
        self.resTypeBtn3 = QRadioButton('Current')
        self.resTypeBtn3.toggled.connect(self._setResType)
        typeBtnGrp = QButtonGroup(self.centralWidget)
        typeBtnGrp.addButton(self.resTypeBtn1)
        typeBtnGrp.addButton(self.resTypeBtn2)
        typeBtnGrp.addButton(self.resTypeBtn3)

        hboxResShowBtn1 = QHBoxLayout()
        # hboxResShowBtn.addWidget(QLabel('type'))
        # hboxResShowBtn.addWidget(self.resType)
        hboxResShowBtn1.addWidget(QLabel('year '))
        hboxResShowBtn1.addWidget(self.resYear)
        hboxResShowBtn1.addWidget(QLabel('month'))
        hboxResShowBtn1.addWidget(self.resMonth)
        hboxResShowBtn1.addWidget(self.resShowMonthBtn)
        hboxResShowBtn1.addWidget(self.resShowDayBtn)
        hboxResShowBtn1.addWidget(self.resShowHourBtn)
        hboxResShowBtn1.addWidget(self.resPrevBtn)

        hboxResShowBtn2 = QHBoxLayout()
        hboxResShowBtn2.addWidget(QLabel('day  '))
        hboxResShowBtn2.addWidget(self.resDay)
        hboxResShowBtn2.addWidget(QLabel('hour '))
        hboxResShowBtn2.addWidget(self.resHour)
        hboxResShowBtn2.addWidget(self.resTypeBtn1)
        hboxResShowBtn2.addWidget(self.resTypeBtn2)
        hboxResShowBtn2.addWidget(self.resTypeBtn3)
        hboxResShowBtn2.addWidget(self.resNextBtn)

        vbox2 = QVBoxLayout()
        vbox2.addLayout(hboxResShowBtn1)
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
        a = 0

    def _setPrevEpoch(self):
        a = 0

    def _setResType(self):
        a = 0

    def _dataVisualization(self):
        self._dynamic_ax1.clear()
        fp = 'MetO-NWS-PHY-hi-CUR_1685448686393.nc'
        # data = netCDF4.Dataset(fp)
        data_set = xr.open_dataset(fp)
        param = self.rawDataType.text()
        year = self.rawDataYear.text()
        month = self.rawDataMonth.text()

        day = self.rawDataDay.text()
        hour = self.rawDataHour.text()
        if param == '' or year == '' or month == '' or day == '' or hour == '':
            data = data_set['vo'][:, :, :, :]
        else:
            if len(month) < 2:
                month = '0' + month
            if len(day) < 2:
                day = '0' + day
            if len(hour) < 2:
                hour = '0' + hour
            time_stamp = year + "-" + str(month) + "-" + str(day) + "T" + str(hour) + ":00:00"
            data = data_set[param].sel(time=time_stamp, method="nearest")
        lat = data_set['lat']
        lon = data_set['lon']
        lon, lat = np.meshgrid(lon, lat)
        self._dynamic_ax1.set_title('Current Velocity')
        # self._dynamic_ax1.pcolor(lon, lat, data['vo'][0, 0, :, :])
        self._dynamic_ax1.pcolor(lon, lat, data[0, 0, :, :])
        self._dynamic_ax1.set_xlabel('lon / deg')
        self._dynamic_ax1.set_ylabel('lat / deg')
        self._dynamic_ax1.axis('equal')
        self._dynamic_ax1.axis('tight')
        self._dynamic_ax1.figure.canvas.draw()

    def _plotResult(self):
        self._dynamic_ax2.clear()
        fp = 'MetO-NWS-PHY-hi-CUR_1685226842264.nc'
        data = netCDF4.Dataset(fp)
        lat = data['lat']
        lon = data['lon']
        lon0 = np.mean(lon)
        lat0 = np.mean(lat)
        lon, lat = np.meshgrid(lon, lat)
        # self._dynamic_ax1.plot.pcolor(lon, lat, data['vo'][0, 0, :, :])
        self._dynamic_ax2.pcolor(lon, lat, data['vo'][0, 0, :, :])
        self._dynamic_ax2.set_xlabel('lon / deg')
        self._dynamic_ax2.set_ylabel('lat / deg')
        self._dynamic_ax2.set_title('Ocean energy distribution map')
        self._dynamic_ax2.axis('equal')
        self._dynamic_ax2.axis('tight')
        self._dynamic_ax2.figure.canvas.draw()

        tt = np.linspace(1, 12, 48)
        xx = np.sin(tt)
        self._dynamic_ax3.plot(tt, xx)
        self._dynamic_ax3.set_title('Ocean energy time series')
        self._dynamic_ax3.set_xlabel('time / month')
        self._dynamic_ax3.set_ylabel('energy')
        self._dynamic_ax3.grid()
        self._dynamic_ax3.axis('tight')
        self._dynamic_ax3.figure.canvas.draw()

        self.textBrowser.append('Tidal energy: = 1000\n')
        self.textBrowser.append('Wave energy: = 1000\n')
        self.textBrowser.append('Current energy: = 1000\n')

        self.textBrowser2.append('Tidal energy variance: = 10\n')
        self.textBrowser2.append('Wave energy variance: = 10\n')
        self.textBrowser2.append('Current energy variance: = 10\n')



