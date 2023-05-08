from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QTextEdit, QTextBrowser, QWidget, QHBoxLayout, QVBoxLayout, QApplication)
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import mapPlot


# 将卫星高度角和方位角转化为平面坐标
def angle_to_xy(elevation, azimuth):
    r = 90 - elevation
    x = r * np.sin(azimuth * 3.1415 / 180)
    y = r * np.cos(azimuth * 3.1415 / 180)
    return [x, y]


# 窗口类
class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 初始化所有变量
        self.ee = []
        self.nn = []
        self.uu = []
        self.h = []
        self.num_of_sat = []
        self.dop = []
        self.time = []
        self.sat_position = []
        self.received_message_num = 0
        self.lat = []
        self.lng = []

        self.setWindowTitle('WQYZCYWZZCLYHJJ')
        self.setGeometry(5, 30, 1355, 730)
        self.browser = QWebEngineView()
        self.url = QtCore.QUrl("./f1.html")
        self.browser.load(self.url)

        dynamic_canvas1 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        dynamic_canvas2 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        dynamic_canvas3 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        # self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(dynamic_canvas, self))
        self._dynamic_ax1 = dynamic_canvas1.figure.subplots()
        self._dynamic_ax2 = dynamic_canvas2.figure.subplots()
        self._dynamic_ax3 = dynamic_canvas3.figure.subplots()

        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setLineWrapMode(QTextEdit.NoWrap)

        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.browser)
        vbox1.addWidget(dynamic_canvas1)
        vbox1.setStretch(0, 1)
        vbox1.setStretch(1, 1)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(dynamic_canvas2)
        hbox1.addWidget(self.textBrowser)
        hbox1.setStretch(0, 3)
        hbox1.setStretch(1, 1)

        vbox2 = QVBoxLayout()
        vbox2.addLayout(hbox1)
        vbox2.addWidget(dynamic_canvas3)
        vbox2.setStretch(0, 3)
        vbox2.setStretch(1, 1)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        hbox.setStretch(0, 1)
        hbox.setStretch(1, 2)

        self.setLayout(hbox)
        self.show()

    def update_sky(self, sat_position):
        self._dynamic_ax1.clear()

        x1 = np.arange(-30, 30, 0.001)
        y1 = np.sqrt(np.power(30, 2) - np.power(x1, 2))
        self._dynamic_ax1.plot(x1, y1, color='b', linestyle=':', linewidth=1)
        self._dynamic_ax1.plot(x1, -y1, color='b', linestyle=':', linewidth=1)
        x2 = np.arange(-60, 60, 0.001)
        y2 = np.sqrt(np.power(60, 2) - np.power(x2, 2))
        self._dynamic_ax1.plot(x2, y2, color='b', linestyle=':', linewidth=1)
        self._dynamic_ax1.plot(x2, -y2, color='b', linestyle=':', linewidth=1)
        x3 = np.arange(-90, 90, 0.001)
        y3 = np.sqrt(np.power(90, 2) - np.power(x3, 2))
        self._dynamic_ax1.plot(x3, y3, color='b', linestyle=':', linewidth=1)
        self._dynamic_ax1.plot(x3, -y3, color='b', linestyle=':', linewidth=1)
        xx = np.arange(-90, 90, 0.001) / 1.414
        self._dynamic_ax1.plot(xx, xx, color='b', linestyle=':', linewidth=1)
        self._dynamic_ax1.plot(xx, -xx, color='b', linestyle=':', linewidth=1)
        xx = np.arange(-95, 95, 0.001)
        yy = xx * 0
        self._dynamic_ax1.plot(xx, yy, color='b', linestyle=':')
        self._dynamic_ax1.plot(yy, xx, color='b', linestyle=':')
        # 绘制卫星位置
        for item in sat_position:
            x, y = angle_to_xy(item[1], item[2])
            self._dynamic_ax1.plot(x, y, 'o', color='g', markersize=2)
            self._dynamic_ax1.text(x + 3, y, item[0])
        self._dynamic_ax1.axis('off')
        self._dynamic_ax1.axis('equal')
        self._dynamic_ax1.figure.canvas.draw()
        a = 0

    # 更新dop与卫星数量图
    def update_dop_sat(self, time, dop, num_of_sat):
        self._dynamic_ax3.clear()
        self._dynamic_ax3.plot(time, dop, label='DOP')
        self._dynamic_ax3.plot(time, num_of_sat, label='Nam of Sat')
        self._dynamic_ax3.set_xlabel('Time / s')
        self._dynamic_ax3.set_ylabel('DOP / Num of Sat')
        self._dynamic_ax3.figure.canvas.draw()

    # 更新测站位置图
    def update_position(self, ee, nn):
        self._dynamic_ax2.plot(ee, nn, 'o', color='b', markersize=3)
        self._dynamic_ax2.axis('equal')
        self._dynamic_ax2.set_xlabel('E / m')
        self._dynamic_ax2.set_ylabel('N / m')
        self._dynamic_ax2.figure.canvas.draw()