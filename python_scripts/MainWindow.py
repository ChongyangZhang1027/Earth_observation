from PyQt5 import QtCore
from PyQt5.QtCore import QRect, QMetaObject, QCoreApplication
from PyQt5.QtWidgets import QMenu, QStatusBar, QWidget, QAction, QMenuBar, QTextBrowser, QTextEdit, QHBoxLayout, \
    QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import matplotlib.pyplot as plt
from matplotlib.backends.backend_template import FigureCanvas
from matplotlib.figure import Figure


class Ui_MainWindow(QWidget):
    def __init__(self):
        super(Ui_MainWindow self).__init__()
        self.statusbar = None
        self.menuTool = None
        self.menuEdit = None
        self.menuFile = None
        self.menuBar = None
        self.centralWidget = None
        self.actionProcess = None
        self.actionSave = None
        self.actionClose = None
        self.actionOpen = None

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 618)

        self.browser = QWebEngineView()
        self.url = QtCore.QUrl("./f1.html")
        self.browser.load(self.url)

        # 加载绘图界面
        self.figure1 = plt.figure(figsize=(9, 3), dpi=100)
        self.dynamic_canvas1 = FigureCanvas(self.figure1)
        dynamic_canvas2 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        dynamic_canvas3 = FigureCanvas(Figure(figsize=(9, 3), dpi=100))
        # self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(dynamic_canvas, self))
        self._dynamic_ax1 = self.dynamic_canvas1.figure.subplots()
        self._dynamic_ax2 = dynamic_canvas2.figure.subplots()
        self._dynamic_ax3 = dynamic_canvas3.figure.subplots()

        # 建立文本框
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setLineWrapMode(QTextEdit.NoWrap)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.dynamic_canvas1)
        hbox1.addWidget(dynamic_canvas2)
        # 左上小图与左下大图放在同一布局内
        vbox1 = QVBoxLayout()
        vbox1.addLayout(hbox1)
        vbox1.addWidget(dynamic_canvas3)

        # 文本框与地图放在同一竖直布局内
        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.browser)
        vbox2.addWidget(self.textBrowser)

        # 两个小竖直布局放在同一水平布局内
        hbox = QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        hbox.setStretch(0, 1)
        hbox.setStretch(1, 1)

        # 设置布局并显示最终窗口
        self.setLayout(hbox)

        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionProcess = QAction(MainWindow)
        self.actionProcess.setObjectName(u"actionProcess")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        MainWindow.setCentralWidget(self.centralWidget)

        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menubar")
        self.menuBar.setGeometry(QRect(0, 0, 1000, 21))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menuBar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuTool = QMenu(self.menuBar)
        self.menuTool.setObjectName(u"menuTool")
        MainWindow.setMenuBar(self.menuBar)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuTool.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionSave)
        self.menuTool.addAction(self.actionProcess)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionProcess.setText(QCoreApplication.translate("MainWindow", u"Process", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuTool.setTitle(QCoreApplication.translate("MainWindow", u"Tool", None))
    # retranslateUi
