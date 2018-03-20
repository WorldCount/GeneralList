#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import AppConfig
import dbfread

__author__ = 'WorldCount'


engine = create_engine(AppConfig.SQLALCHEMY_DATABASE_URI)
# Session = sessionmaker()
# Session.configure(bind=engine)
# db = Session()
#
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base(bind=engine)
Base.query = session.query_property()


def init_db(fill_index=None, fill_config=None):
    print('Создаю БД...')
    from app import models
    Base.metadata.create_all(bind=engine)
    if fill_index: _fill_table_index()
    if fill_config: _fill_table_config()
    print('... Cоздана: {}'.format(AppConfig.DATABASE_PATH))


def recreate_db(fill_index=None, fill_config=None):
    print('Пересоздаю БД:')
    if os.path.exists(AppConfig.DATABASE_PATH):
        print('Удаляю старую БД...')
        os.remove(AppConfig.DATABASE_PATH)
        print('... Удалена: {}'.format(AppConfig.DATABASE_PATH))
        init_db(fill_index, fill_config)


def _fill_table_index():
    print('Заполняю таблицу с индексами...')
    from app.post_data.updater import Updater
    from app.models import Index
    updater = Updater(AppConfig.TEMP_DIR)
    path = updater.download_update()
    if not path:
        print('... Возникла ошибка при скачивании справочника. Пропуск')
    else:
        dbf = dbfread.DBF(path, encoding='cp866')
        print('... Найдено индексов: {}. Загружаю.'.format(len(dbf)))
        for row in dbf:
            region = row['REGION'] or row['AUTONOM']
            index = Index(row['INDEX'], row['OPSNAME'], row['OPSSUBM'], region)
            session.add(index)
        print('... Сохраняю.')
        session.commit()
        print('... Готово.')


def _fill_table_config():
    print('Заполняю таблицу с настройками...')
    from app.models import Config
    config = Config('auto_complete_reception', True)
    session.add(config)
    print('... Сохраняю.')
    session.commit()
    print('... Готово.')
