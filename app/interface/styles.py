#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import (QStyle, QProxyStyle)


__author__ = 'WorldCount'


class AppStyle(QProxyStyle):

    def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):
        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return 24
        else:
            return QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option, widget)