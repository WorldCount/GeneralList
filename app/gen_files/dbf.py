#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import date
from dbfread import DBF
from app.wcutils.files import get_file_name
from app.gen_files.reader import Reader
from app.models import (ListRpo, Rpo, Error)
from app import session


__author__ = 'WorldCount'


# Парсер файлов DBF
class GenDbfReader(Reader):

    def __init__(self, link, preload=False, encoding='cp866', list_date: date = None, find_error=False):
        """
        :param link: Путь к файлу DBF
        :param preload: Предзагрузка файла
        :param encoding: Кодировка вывода
        :param find_error: Искать ошибки в РПО
        """
        super(GenDbfReader, self).__init__(link)

        self._encoding = encoding
        self._name = ''
        self._num_list = ''
        self._author = 'Неизв.'
        self._dir = ''
        self._header = ''
        self._dbf = None
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
            self._dir, self._name = os.path.split(self._link)
            self._num_list = self._num_list_parse()
            self._dbf = DBF(self._link, load=True, encoding=self._encoding)
            return True
        return False

    # Инициализация заголовков таблицы
    def _init_header(self):
        self._header = []
        self._header = self._dbf.field_names

    # Читает остальные данные по таблице
    def _read_data(self):

        for row_ind, row in enumerate(self._dbf):
            mass = row['MASS']
            mass_rate = self._mass_rate_parse(row['MASSRATE'])
            address = self._address_parse(row['CITY'])
            reception = self._address_parse(row['ADDRESSEE'])

            rpo = Rpo(barcode=row['BARCODE'], index=row['INDEXTO'], address=address, reception=reception,
                      mass=mass, mass_rate=mass_rate, num_string=row_ind + 1)
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
        return get_file_name(self._link)[5:]

    # Парсит весовой сбор
    def _mass_rate_parse(self, mass_rate):
        if str(mass_rate)[-2:] == "00":
            return float(mass_rate) / 100
        return float(mass_rate) / 10

    # Парсит адрес
    def _address_parse(self, address):
        """
        :param address: Строка с адресом
        :return: Распарсенная строка с адресом
        """
        return address.replace("\n", " ").replace("|", " ")

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
        return Error.query.filter(Error.rpo.has(list_id=self._list_rpo.id)).all()

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