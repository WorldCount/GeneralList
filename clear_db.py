#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from app import (init_db, recreate_db)
from config import AppConfig

__author__ = 'WorldCount'


def test_updater():
    from app.post_data.updater import Updater
    updater = Updater()
    path = updater.download_update()
    print('Путь: {}'.format(path))


if __name__ == '__main__':

    if not os.path.exists(AppConfig.DATABASE_PATH):
        init_db(True, True)
    else:
        recreate_db(True, True)
