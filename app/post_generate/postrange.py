#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import binascii
from datetime import datetime

__author__ = 'WorldCount'


"""
Набор функций для генерации файла с диапазоном
"""

_FORMAT_LIST = ['<?xml version="1.0" encoding="UTF-8"?>',
                '<ns:Range xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns="http://russianpost.org"',
                ' xsi:schemaLocation="http://russianpost.org range.xsd" Inn="{inn}" IndexFrom="{index_from}"',
                ' DateInfo="{date_info}" CRC="{crc}">',
                '<ns:Segment NumMonth="{num_month}" NumBeg="{num_beg}" NumEnd="{num_end}" State="{state}"/>',
                '</ns:Range>']
_FORMAT_STRING = ''.join(_FORMAT_LIST)


# Возвращает CRC хеш из списка с данными
def gen_crc_hash(list_data):
    str_data = [str(line) for line in list_data]
    data_to_str = ''.join(str_data)
    crc = (binascii.crc32(bytearray(data_to_str, 'utf8')) & 0xFFFFFFFF)
    crc_hash = '%02x' % crc
    return crc_hash.upper()


# Возвращает имя генерируемого файла
def gen_file_name(inn, ops_num, date_gen):
    try:
        date_to_str = date_gen.strftime('%Y%m%d%H%M%S')
        inn = str('%012d' % int(inn))
        name = '%s_%s_%s.xml' % (inn, ops_num, date_to_str)
        return name
    except (AttributeError, TypeError):
        return False


# Возвращает заполненное тело файла
def get_xml_body(inn, ops_num, month, num_begin, num_end, date, state, crc):
    res = _FORMAT_STRING.format(inn=inn, index_from=ops_num, date_info=date, num_month=month,
                                num_beg=num_begin, num_end=num_end, state=state, crc=crc)
    return res


# Генерирует файл с диапазоном в папку
def gen_postrange_file(inn, ops_num, month, num_begin, num_end, date_gen=None, state="1", path=None):
    if not path:
        path = os.path.dirname(__file__)

    if not os.path.exists(path):
        os.makedirs(path)

    if not date_gen:
        date_gen = datetime.today()

    str_date = date_gen.strftime('%d.%m.%Y %H:%M:%S')
    crc_data = [inn, ops_num, str_date, month, num_begin, num_end, state]
    crc = gen_crc_hash(crc_data)

    file_name = gen_file_name(inn, ops_num, date_gen)
    body = get_xml_body(inn, ops_num, month, num_begin, num_end, str_date, state, crc)

    file_path = os.path.join(path, file_name)
    with open(file_path, 'w') as save_file:
        save_file.write(body)


# Получает номер месяца за указаную дату
def get_month_num(date):
    month = (date.year - 2000) * 12 + date.month
    return month


# Получает дату указанного месяца
def get_month_date(month_num):

    start_year = 2000
    start_month = 0
    rem_year = 0

    if month_num == 0:
        return datetime(start_year, 1, 1)

    if month_num < 0:
        month_num *= -1

    month_range = month_num % 12
    if month_range == 0:
        rem_year = 1

    start_month += month_range or 12
    start_year += month_num // 12 - rem_year

    return datetime(start_year, start_month, 1)






if __name__ == '__main__':

    import sys
    import argparse

    parser = argparse.ArgumentParser(add_help=True, description='Генератор файла дипазонов')
    parser.add_argument('--inn', '-i', type=str, action='store', dest='INN', help='Номер ИНН организации')
    parser.add_argument('--ops', '-o', type=str, action='store', dest='OPS', help='Номер ОПС')
    parser.add_argument('--month', '-m', type=str, action='store', dest='MONTH', help='Номер месяца отправки')
    parser.add_argument('--begin', '-b', type=str, action='store', dest='BEGIN', help='Начальный номер отправления')
    parser.add_argument('--end', '-e', type=str, action='store', dest='END', help='Конечный номер отправления')
    parser.add_argument('--state', '-s', type=str, action='store', dest='STATE', default="1",
                        help='Статус диапазона. 1 - свободен, 3 - занят')
    parser.add_argument('--dir', '-d', type=str, action='store', dest='PATH', help='Путь к папке, для генерации файла')
    # Парсим аргументы
    data = parser.parse_args()
    # Ошибки
    errors = []
    if not data.INN:
        errors.append('Не указан ИНН организации')
    if not data.OPS:
        errors.append('Не указан номер ОПС')
    if not data.MONTH:
        errors.append('Не указан номер месяца')
    if not data.BEGIN:
        errors.append('Не указан начальный номер отправления')
    if not data.END:
        errors.append('Не указан конечный номер отправления')

    # Если есть ошибки, то выводим их и завершаем работу
    if len(errors) > 0:
        for error in errors:
            sys.stderr.write('%s\n' % error)
        sys.exit(2)
    else:
        if not data.PATH:
            gen_postrange_file(data.INN, data.OPS, data.MONTH, data.BEGIN, data.END, state=data.STATE, path='.\GEN')
        else:
            gen_postrange_file(data.INN, data.OPS, data.MONTH, data.BEGIN, data.END, state=data.STATE, path=data.PATH)
