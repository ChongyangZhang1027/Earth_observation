# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file 'twet_maineYwMoB.ui'
#
# Created by: Qt User Interface Compiler version 5.15.2
#
# WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
from PyQt5.QtWidgets import QMainWindow
from MainWindow import Ui_MainWindow
from PyQt5 import QtWidgets
import sys


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        print("initialize")
        self.setupUi(self)

    def setup_ui(self):
        pass

    def binding(self):
        pass


app = QtWidgets.QApplication(sys.argv)
window = Window()
ui = Ui_MainWindow()
ui.setupUi(window)
window.show()
sys.exit(app.exec_())
