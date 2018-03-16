#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication)
from app.interface.windows import AppWindow
from app.interface.styles import AppStyle

__author__ = 'WorldCount'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #style =  QStyleFactory()
    style =  AppStyle('Fusion')
    #app.setStyle(style.create('Fusion'))
    app.setStyle(style)
    win = AppWindow()
    win.show()
    sys.exit(app.exec_())
