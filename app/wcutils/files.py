#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import glob


__author__ = 'WorldCount'


"""
Работа с файлами
"""


# Создает директории из списка
def create_dirs(list_dirs):
    """
    :param list_dirs: Список директорий
    :return: Результат работы
    """
    if type(list_dirs) == list:
        for new_dir in list_dirs:
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
        return True
    return False


# Возвращает путь к папке файла
def get_file_dir(path):
    """
    :param path: Путь к файлу
    :return: Путь к папке
    """
    return os.path.abspath(os.path.dirname(path))


# Ищет файлы в папке
def find_files(path_to_dir, ext='*.*F'):
    """
    :param path_to_dir: Путь до папки
    :param ext: Расширения файлов
    :return: Список файлов
    """
    files = glob.glob(os.path.join(path_to_dir, ext))
    return files


# Объединяет списки файлов
def join_files(*args):
    """
    :param args: Списки с файлами
    :return: Объединеный список файлов
    """
    data = []
    for arg in args:
        data.extend(arg)
    return data


# Возвращает название файла с расширением
def get_full_file_name(path_to_file):
    """
    :param path_to_file: Путь до файла
    :return: Название файла с раширением
    """
    return path_to_file.split('\\')[-1]


# Возвращает название файла без расширения
def get_file_name(path_to_file):
    """
    :param path_to_file: Путь до файла
    :return: Название файла без расширения
    """
    return get_full_file_name(path_to_file).split('.')[0]


# Возвращает расширение файла
def get_file_ext(path_to_file):
    """
    :param path_to_file: Путь до файла
    :return: Расширение файла
    """
    return path_to_file.split('\\')[-1].split('.')[-1]
