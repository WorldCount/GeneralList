#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from urllib.request import urlretrieve
from zipfile import ZipFile
import dbfread

__author__ = 'WorldCount'


class Updater:

    def __init__(self, temp_dir_path=None):
        self.path = os.path.dirname(__file__)
        self.dir = temp_dir_path or os.path.join(self.path, 'TEMP')
        self.name = 'index.dbf'
        self.url = 'http://vinfo.russianpost.ru/database/PIndx.zip'

        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

    def download_update(self):
        temp_name = 'index.zip'
        path_to_zip = os.path.join(self.dir, temp_name)

        # Скачиваем архив с индексами
        try:
            urlretrieve(self.url, path_to_zip)
        except Exception:
            return False
        # Распаковываем архив
        if os.path.exists(self.dir):
            with ZipFile(path_to_zip) as my_zip:
                name = my_zip.namelist()[0]
                my_zip.extract(name, self.dir)
            self.remove_file(path_to_zip)
            return os.path.join(self.dir, name)
        else:
            return False

    def remove_file(self, path_to_file):
        if os.path.exists(path_to_file):
            try:
                os.remove(path_to_file)
            except Exception:
                return False
        return True
