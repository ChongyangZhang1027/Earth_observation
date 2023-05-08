# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file 'twet_maineYwMoB.ui'
#
# Created by: Qt User Interface Compiler version 5.15.2
#
# WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
import sys

from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow

if __name__ == '__main__':
    # 建立主窗口
    app = QApplication(sys.argv)
    win = MainWindow()
    # 开启数据监听多线程
    # thread_01 = Thread(target=win.data_receive)
    # thread_01.start()
    # 退出
    app.exit(app.exec_())
