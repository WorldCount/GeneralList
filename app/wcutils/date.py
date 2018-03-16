#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime


__author__ = 'WorldCount'


"""
Работа с датами
"""


# Форматирует дату
def format_date(in_date):
    """
    :param in_date: Дата
    :return: Строка с отформатированной датой или False
    """
    if type(in_date) == datetime.datetime:
        return in_date.strftime("%d.%m.%Y %H:%M:%S")
    elif type(in_date) == datetime.date:
        return in_date.strftime("%d.%m.%Y")
    return False
