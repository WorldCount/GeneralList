#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from datetime import date
from xlrd import open_workbook
from app.gen_files.reader import Reader
from app.models import (ListRpo, Rpo, Error)
from app import session


__author__ = 'WorldCount'


_FILE_NUM_PATTERN = re.compile(r'[0-9]+-[0-9]+')


# Парсер файлов Excel
class GenExcelReader(Reader):

    def __init__(self, link, read_name_list=None, header_row_num=5, column_num=6, preload=False, list_date: date = None, find_error=False):
        """
        :param link: Путь к файлу Excel
        :param read_name_list: Название или номер листа который будем читать
        :param header_row_num: На какой строке находится заголовок таблицы
        :param column_num: По какую колонку считывать данные
        :param preload: Предзагрузка файла
        :param find_error: Искать ошибки в РПО
        """
        super(GenExcelReader, self).__init__(link)

        self._workbook = None
        self._worksheet = None
        self._read_name_list = read_name_list
        self._header_row_num = header_row_num
        self._column_num = column_num
        self._current_worksheet_name = ''
        self._name = ''
        self._author = ''
        self._num_list = ''
        self._dir = ''
        self._header = []
        self._preload = preload
        self._find_error = find_error
        self._date = list_date or date.today()
        self._list_rpo = ListRpo(list_date=self._date)
        session.add(self._list_rpo)

        if self._preload:
            self._preload_file()

    # Предзагрузка данных по листу
    def _preload_file(self):
        if os.path.exists(self._link):
            self._workbook = open_workbook(self._link)
            # Получаем лист
            if self._read_name_list:
                if type(self._read_name_list) == int:
                    self._worksheet = self._workbook.sheet_by_index(self._read_name_list)
                elif type(self._read_name_list) == str:
                    self._worksheet = self._workbook.sheet_by_name(self._read_name_list)
                else:
                    self._worksheet = self._workbook.sheets()[0]
            else:
                self._worksheet = self._workbook.sheets()[0]

            self._current_worksheet_name = self._worksheet.name
            self._dir, self._name = os.path.split(self._link)
            self._author = self._workbook.user_name
            self._num_list = self._num_list_parse()
            return True
        return False

    # Инициализация заголовков таблицы
    def _init_header(self):
        row = self._worksheet.row(self._header_row_num)
        self._header = [col.value for col in row[0:self._column_num + 1]]

        # Читает остальные данные по таблице
    def _read_data(self):

        for row_ind in range(self._header_row_num + 1, self._worksheet.nrows):
            first = self._worksheet.cell(row_ind, 0)
            if first.value == "": break
            # Данные таблицы
            barcode = self._barcode_parse(self._worksheet.cell(row_ind, 1).value)
            index = self._index_parse(self._worksheet.cell(row_ind, 2).value)
            address = self._address_parse(self._worksheet.cell(row_ind, 3).value)
            reception = self._reception_parse(self._worksheet.cell(row_ind, 4).value)
            mass = int(self._worksheet.cell(row_ind, 5).value)
            mass_rate = self._mass_rate_parse(self._worksheet.cell(row_ind, 6).value)

            rpo = Rpo(barcode=barcode, index=index, address=address, reception=reception,
                      mass=mass, mass_rate=mass_rate, num_string=row_ind - self.header_row_num)
            rpo.double = rpo.is_double()

            self._list_rpo.add_rpo(rpo)

            if self._find_error:
                rpo.find_error()

    # Загружает и парсит файл
    def load(self):
        if not self._preload:
            self._preload_file()
        self._init_header()

        self._list_rpo.num = self._num_list
        self._list_rpo.author = self._author

        self._read_data()

    # Парсит номер списка
    def _num_list_parse(self):
        unparse = self._worksheet.row(1)[0].value
        find = _FILE_NUM_PATTERN.findall(unparse)
        if len(find) > 0:
            return find[0].replace("-", '')
        return False

    # Парсит индекс
    def _index_parse(self, index):
        """
        :param index: Строка с индексом
        :return: Распарсенная строка с индексом
        """
        return str(index)[0:6]

    # Парсит ШПИ отправления
    def _barcode_parse(self, string):
        """
        :param string: Строка с ШПИ
        :return: Распарсенная строка с ШПИ
        """
        data = string.split('\n')
        if len(data) > 1:
            return data[1].replace(' ', '')
        return False

    # Парсит плату за отправление
    def _mass_rate_parse(self, mass_rate):
        """
        :param mass_rate: Плата за вес
        :return: Распарсенная плата за вес в float
        """
        if type(mass_rate) == str:
            mass_rate = mass_rate.replace(',', '.')
            return float(mass_rate)
        return mass_rate

    # Парсит адрес
    def _address_parse(self, address):
        """
        :param address: Строка с адресом
        :return: Распарсенная строка с адресом
        """
        return address.replace("\n", " ").replace("|", " ")

    # Парсит получателя
    def _reception_parse(self, reception):
        """
        :param reception: Строка с получателем
        :return: Распарсенная строка с получателем
        """
        data = reception.split("\n")
        if len(data) > 1: return data[0].replace("|", " ")
        return data.replace("|", " ")

    @property
    def workbook(self):
        return self._workbook

    @property
    def worksheet(self):
        return self._worksheet

    @property
    def name_list(self):
        return self._read_name_list

    @property
    def header_row_num(self):
        return self._header_row_num

    @property
    def column_num(self):
        return self._column_num

    @property
    def current_worksheet_name(self):
        return self._current_worksheet_name

    @property
    def name(self):
        return self._name

    @property
    def date(self):
        return self._date

    @property
    def dir(self):
        return self._dir

    @property
    def header(self):
        return self._header

    @property
    def data(self):
        return self._list_rpo.all_rpo.all()

    @property
    def mass(self):
        return self._list_rpo.mass

    @property
    def mass_rate(self):
        return self._list_rpo.mass_rate

    @property
    def author(self):
        return self._list_rpo.author

    @property
    def num_list(self):
        return self._list_rpo.num

    @property
    def errors(self):
        return Error.query.filter(Error.rpo.has(list_id = self._list_rpo.id)).all()

    @property
    def mail_type(self):
        return self._list_rpo.mail_type

    @property
    def object(self):
        return self._list_rpo

    @property
    def rpo_count(self):
        return self._list_rpo.rpo_count

    @property
    def double_count(self):
        return self._list_rpo.double_count

    @property
    def error_count(self):
        return self._list_rpo.error_count
