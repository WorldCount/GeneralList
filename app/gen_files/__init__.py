#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
from.excel import GenExcelReader
from .dbf import GenDbfReader
from app.wcutils.files import get_file_ext

__author__ = 'WorldCount'


class GenFileReader:

    def __init__(self, link, read_name_list=None, header_row_num=5, column_num=6, preload=False,
                 encoding='cp866', list_date: date=None, find_error=False):
        """
        :param link: Путь к файлу DBF, XLS, XLSX
        :param read_name_list: Название или номер листа который будем читать
        :param header_row_num: На какой строке находится заголовок таблицы
        :param column_num: По какую колонку считывать данные
        :param preload: Предзагрузка файла
        :param encoding: Кодировка вывода
        :param find_error: Искать ошибки в РПО
        """

        self._link = link
        self._read_name_list = read_name_list
        self._header_row_num = header_row_num
        self._column_num = column_num
        self._preload = preload
        self._encoding = encoding
        self._find_error = find_error
        self._date = list_date or date.today()
        self.ext = get_file_ext(self._link)

    def parse(self):
        parser = None

        if self.ext == 'dbf':
            parser = GenDbfReader(self._link, self._preload, self._encoding, self._date, self._find_error)
            parser.load()
        elif self.ext in ('xls', 'xlsx'):
            parser = GenExcelReader(self._link, self._read_name_list,
                                    self._header_row_num, self._column_num, self._preload, self._date, self._find_error)
            parser.load()
        else:
            return parser
        return parser
