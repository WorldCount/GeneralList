#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from app.wcutils.files import find_files

__author__ = 'WorldCount'


if __name__ == '__main__':
    from config import AppConfig
    files = find_files(AppConfig.TEMP_DIR, '*.ini')
    for file in files:
        print('Удален: {}'.format(file))
        os.remove(file)
