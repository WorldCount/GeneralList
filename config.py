#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ctypes
from app.wcutils.files import (get_file_dir, create_dirs)
from PyQt5.QtGui import QFont

__author__ = 'WorldCount'


basedir = get_file_dir(__file__)

# ПРИЛОЖЕНИЕ
myappid = u'worldcount.mmp4.genlist.1'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


# Класс настроек
class AppConfig:

    # Название приложения
    APP_NAME = 'Списки Ген.Прокуратуры'
    # Версия приложения
    APP_VERSION = '1.0.0.0'
    # Номер ОПС
    OPS_NUM = 125993
    # Маски файлов для загрузки
    FILE_MASKS = ['*.xls', '*.xlsx', '*.dbf']
    # Пути к файлам
    IN_FILE_DIR = os.path.join(basedir, 'in_list')
    OUT_FILE_DIR = os.path.join(basedir, 'out_list')
    # БАЗА
    DATABASE_PATH = os.path.join(basedir, 'database.db')
    # Подключение к БД
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}?check_same_thread=False'.format(DATABASE_PATH)
    # Папка для временных файлов
    TEMP_DIR = os.path.join(basedir, 'TEMP')

    FONT = QFont('Consolas', 11)
    WIDGET_HEIGHT = 32
    BUTTON_WIDTH = 100
    # Раскрашивать строки в таблице
    COLORIZE = True


# Класс настроек тарификатора
class TarificatorConfig:

    # Начальная плата за письмо
    START_MAIL_TARIF = 41.00
    # Начальный вес письма, в граммах
    START_MAIL_WEIGHT = 20
    # Конечный вес письма, в граммах
    END_MAIL_WEIGHT = 100

    # Начальная плата за бандероль
    START_PARCEL_TARIF = 60.00
    # Начальный вес бандероли, в граммах
    START_PARCEL_WEIGTH = 100
    # Конечный вес бандероли, в граммах
    END_PARCEL_WEIGHT = 2000

    # Размер шага веса, в граммах
    WEIGHT_STEP = 20
    # Плата за шаг
    PAY_PER_STEP = 2.50


# Настройки отправителя
class SenderConfig:

    # ИНН организации
    INN = '7710146102'
    # КПП организации
    KPP = '771001001'
    # Название отправителя
    SNDR = 'ГЕНЕРАЛЬНАЯ ПРОКУРАТУРА'
    # Хз что это...
    DEEP_CODE = '000000000'
    # Телефон организации
    SNDR_TEL = ''

    # Категория отправителя, значения:
    # 1 - Население, 2 - Бюджетная организация, 3 - Хозрасчетная организация,
    # 4 - Международный оператор, 5 - Корпоративный клиент, 6 - Федеральный клиент
    SEND_CTG = 2

    # Классификация отправления, значения: 1 - Внутренняя, 2 - Международная
    DIRECT_CTG = 1

    # Способ оплаты, значения:
    # 1 - Наличная, 2 - Безналичная, 4 - Бесплатно,
    # 8 - Пластиковая карта, 16 - Гос.Знаки(Марки), 32 - Предоплата(Аванс), 64 - оплачено МЖД оператору
    PAY_TYPE = 2
    # Какая-то бесполезная хуета
    PAY_TYPE_NOT = 2

    # Способ пересылки, значения: 1 - Наземный, 2 - Авиа, 3 - Комбинированный, 4 - Системой ускоренной почты
    TRANS_TYPE = 1

    # Почтовые отметки, значения: 0 - Без отметки, 1 - С простым уведомлением, 2 - С заказным уведомлением
    POST_MARK = 0

    # Разряд отправления, значения:
    # 0 - Без разряда, 1 - Правительственное, 2 - Воинское, 3 - Служебное,
    # 4 - Судебное, 5 - Президентское, 6 - Кредитное
    MAIL_RANK = 0

    # Номер договора
    NUM_CONTRACT = '41009'
    # Тип смс уведомления (мин - 0, макс - 1, значения: [1, 2, 1+2, Пусто])
    SMS_NOTICES = ''

    # АДРЕС
    # Тип адреса, значения:
    # 1 - стандартный, 2 - а/я, 3 - до востребования, 4 - гостиница,
    # 5 - войсковая часть, 6 - войсковая часть ЮЯ, 7 - полевая часть
    ADDRESS_TYPE_SNDR = 1
    # Номер типа адреса, обязательно для а/я
    NUM_ADDRESS_TYPE_SNDR = ''
    # Почтовый индекс отправителя
    INDEX_SNDR = 125993
    # Область, регион отправителя
    REGION_SNDR = 'МОСКВА'
    # Район отправителя
    AREA_SNDR = ''
    # Населеный пункт отправителя
    PLACE_SNDR = 'МОСКВА'
    # Внутригородской элемент: квартал\спутник\поселение\микрорайон\территория
    LOCATION_SNDR = ''
    # Улица отправителя
    STREET_SNDR = ''
    # Номер здания, обязательно для стандартный и гостиница
    HOUSE_SNDR = ''
    # Литера
    LETTER_SNDR = ''
    # Дробь
    SLASH_SNDR = ''
    # Корпус
    CORPUS_SNDR = ''
    # Строение
    BUILDING_SNDR = ''
    # Название гостиницы, обязательно для гостиницы
    HOTEL_SNDR = ''
    # Номер помещения
    ROOM_SNDR = ''

    # Формат файла
    DOC_VERSION = 'RTM0003-11-16'


create_dirs([AppConfig.TEMP_DIR])
