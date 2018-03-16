#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

__author__ = 'WorldCount'


"""
Работа с нумерацией почтового файла
"""

_FIRST_PATTERN = re.compile(r'[0-9]+')
_SECOND_PATTERN = re.compile(r'[0-9]+F')


# Парсит имя файла
def parse_name(file_name):
    first = _FIRST_PATTERN.findall(file_name)
    second = _SECOND_PATTERN.findall(file_name)

    if len(first) < 1 or len(second) < 1:
        return False

    name = '%s.%s' % (first[0], second[-1])
    name_len = len(name)

    if name_len == 12:
        return name
    elif name_len == 11:
        return '1%s' % name
    else:
        return False


# Получает номер файла
def get_number(file_name):
    name = parse_name(file_name)

    if not name:
        return False

    try:
        return int('%s%s' % (name[6:8], name[9:11]))
    except ValueError:
        return False


# Генерирует имя файла
def gen_name(ops_num, file_num):

    try:
        _ = int(ops_num)
        num = int(file_num)
    except ValueError:
        return False

    if num <= 0 or num > 9999:
        return False

    number = '%04d' % num
    ops = str(ops_num)

    if len(ops) != 6:
        return False

    return '%s%s.%sF' % (ops, number[:2], number[2:])


# Изменяет номер файла на указанное число
def change_name(file_name, num):
    name = parse_name(file_name)

    if not name:
        return False

    ops = name[:6]

    try:
        number = get_number(file_name) + int(num)
    except ValueError:
        return False

    if number < 0 or number > 9999:
        return False
    return gen_name(ops, number)


# Повышает номер файла на указанное число
def increment_name(file_name, num=1):
    try:
        inc_num = int(num)
        if num < 0:
            inc_num *= -1
        return change_name(file_name, inc_num)
    except ValueError:
        return False


# Понижает номер файла на указанное число
def decrement_name(file_name, num=1):
    try:
        dec_num = int(num)
        if num > 0:
            dec_num *= -1
        return change_name(file_name, dec_num)
    except ValueError:
        return False


# Создает список с номерами файлов
def create_name_list(ops_num, in_num, out_num):
    res = []

    try:
        ops = str(ops_num)
        if len(ops) < 6:
            return False

        for i in range(int(in_num), int(out_num) + 1):
            name = gen_name(ops, i)
            if name:
                res.append(name)
        return res

    except ValueError:
        return False


# Проверяет пропуски файлов
def check_miss_file(list_files):
    if len(list_files) <= 1:
        return []

    res = []
    list_files.sort()

    name_in = parse_name(list_files[0])
    name_out = parse_name(list_files[-1])

    if not name_in or not name_out:
        return False

    ops = name_in[:6]
    num_in = get_number(name_in)
    num_out = get_number(name_out)

    list_compare = create_name_list(ops, num_in, num_out)
    for file_name in list_compare:
        if file_name not in list_files:
            res.append(file_name)

    return res


# Проверяет пропуски файлов в словаре
def check_miss_dict(dict_files):
    res_list = []

    for file_key in dict_files.keys():
        miss_list = check_miss_file(dict_files[file_key])
        if len(miss_list) > 0:
            res_list.extend(miss_list)
    return res_list


# Проверяет пропуски файлов в списке
def check_miss_list(list_files):
    return check_miss_dict(list_to_dict(list_files))


# Переводит список в словарь
def list_to_dict(list_files):
    res_dict = {}

    for file_name in list_files:

        name = parse_name(file_name)

        if not name:
            continue

        current_key = int(name.split('.')[0])
        num_key = current_key

        if num_key - 1 in res_dict.keys():
            current_key -= 1
        elif num_key + 1 in res_dict.keys():
            current_key += 1
        else:
            pass

        if current_key not in res_dict.keys():
            temp_dict = {current_key: [name]}
            res_dict.update(temp_dict)
        else:
            res_dict[current_key].append(name)

    return res_dict


# Переводит словарь в список
def dict_to_list(dict_files):
    res_list = []
    for file_key in dict_files.keys():
        new_list = dict_files[file_key]
        if len(new_list) > 0:
            res_list.extend(new_list)
    res_list.sort()
    return res_list


# Загружает из файла список с именами файлов
def load_list_files(file_path):
    res_list = []

    if not os.path.exists(file_path):
        return False

    with open(file_path, 'r') as load_file:
        for line in load_file.readlines():
            res_list.append(line.strip())
    return res_list


# Сохраняет в файл список с именами файлов
def save_list_files(file_path, list_files):
    with open(file_path, 'w') as save_file:
        for line in list_files:
            save_file.write('%s\n' % line)
