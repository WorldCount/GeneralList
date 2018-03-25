#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtWidgets import QApplication
from app.interface.windows import AppWindow
from app.interface.styles import AppStyle
from app.wcutils.files import get_file_dir
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize


__author__ = 'WorldCount'


def get_app_icon() -> QIcon:
    current = get_file_dir(__file__)
    # Иконка приложения
    APP_ICON = QIcon()
    APP_ICON.addFile(os.path.join(current, 'icon', 'icon_016.png'), QSize(16, 16))
    APP_ICON.addFile(os.path.join(current, 'icon', 'icon_032.png'), QSize(32, 32))
    APP_ICON.addFile(os.path.join(current, 'icon', 'icon_048.png'), QSize(48, 48))
    APP_ICON.addFile(os.path.join(current, 'icon', 'icon_128.png'), QSize(128, 128))
    return APP_ICON


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(get_app_icon())
    style =  AppStyle('Fusion')
    app.setStyle(style)
    win = AppWindow()
    win.show()
    sys.exit(app.exec_())
