#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import date, datetime
from config import SenderConfig as S, AppConfig
from app.models import (ListRpo, Rpo)
from configparser import ConfigParser
from app import session


__author__ = 'WorldCount'


class RTM:

    # Поля секции: Main
    main_fields = []
    # Поля секции: Sender
    sender_fields = []
    # Поля секции: Summary
    summary_fields = []
    # Поля секции: DocVersion
    docversion_fields = []

    # Заголовок TXT файла
    header = []

    def __init__(self):
        self.version = 'RTM0003'

        # Словарь секции: Main
        self.main_dict = {}
        # Словарь секции: Sender
        self.sender_dict = {}
        # Словарь секции: Summary
        self.summary_dict = {}
        # Словарь секции: DocVersion
        self.docversion_dict = {'DocVersion': self.version}

    # Создает TXT файл
    def create_txt(self, path_to_dir):
        """
        :param path_to_dir: Путь к папке сохранения
        :return:
        """
        pass

    # Создает INI файл
    def create_ini(self, path_to_dir):
        """
        :param path_to_dir: Путь к папке сохранения
        :return:
        """
        pass

    # Возвращает дату в почтовом формате
    @staticmethod
    def get_date(in_date=None):
        """
        :param in_date: Дата или ничего
        :return: Строка с датой
        """
        if in_date and type(in_date) in (date, datetime):
            return in_date.strftime("%Y%m%d")
        return date.today().strftime("%Y%m%d")


class GenRTMFormat(RTM):

    def __init__(self, list_rpo: ListRpo):
        super(GenRTMFormat, self).__init__()

        # Версия формата
        self.version = 'RTM0003-11-16'

        # Объект с данными по списку models.ListRpo
        self._list_rpo = list_rpo

        # DeliveryRateSum - общая сумма платы за пересылку БЕЗ НДС (в копейках)
        self.mass_rate = self.format_int(self._list_rpo.mass_rate)
        # DeliveryRateVAT - НДС от общей платы за пересылку (в копейках)
        self.nds_mass_rate = int((round(self._list_rpo.mass_rate / 100 * 18, 2)) * 100)
        # DeliveryRateTotal - общая сумма платы за пересылку С НДС (в копейках)
        self.sum_mass_rate = self.mass_rate + self.nds_mass_rate

        # MAIN
        # Поля секции: Main
        self.main_fields = ['Inn', 'Kpp', 'DepCode', 'SndrTel', 'SendCtg', 'SendDate', 'ListNum', 'IndexFrom',
                            'MailType', 'MailCtg', 'DirectCtg', 'PayType', 'PayTypeNot', 'TransType', 'PostMark',
                            'MailRank', 'NumContract', 'SMSNoticeS']
        # Словарь секции: Main
        self.main_dict = {'Inn': S.INN, 'Kpp': S.KPP, 'DepCode': S.DEEP_CODE, 'SndrTel': S.SNDR_TEL,
                          'SendCtg': S.SEND_CTG, 'SendDate': RTM.get_date(self._list_rpo.date),
                          'ListNum': self._list_rpo.num, 'IndexFrom': AppConfig.OPS_NUM,
                          'MailType': self._list_rpo.mail_type, 'MailCtg': 1,
                          'DirectCtg': S.DIRECT_CTG, 'PayType': S.PAY_TYPE, 'PayTypeNot': S.PAY_TYPE_NOT,
                          'TransType': S.TRANS_TYPE, 'PostMark': S.POST_MARK, 'MailRank': S.MAIL_RANK,
                          'NumContract': S.NUM_CONTRACT, 'SMSNoticeS': S.SMS_NOTICES}

        # SENDER
        # Поля секции: Sender
        self.sender_fields = ['Sndr', 'AddressTypeSndr', 'NumAddressTypeSndr', 'IndexSndr', 'RegionSndr', 'AreaSndr',
                              'PlaceSndr', 'LocationSndr', 'StreetSndr', 'HouseSndr', 'LetterSndr', 'SlashSndr',
                              'CorpusSndr', 'BuildingSndr', 'HotelSndr', 'RoomSndr']
        # Словарь секции: Sender
        self.sender_dict = {'Sndr': S.SNDR, 'AddressTypeSndr': S.ADDRESS_TYPE_SNDR,
                            'NumAddressTypeSndr': S.NUM_ADDRESS_TYPE_SNDR, 'IndexSndr': S.INDEX_SNDR,
                            'RegionSndr': S.REGION_SNDR, 'AreaSndr': S.AREA_SNDR, 'PlaceSndr': S.PLACE_SNDR,
                            'LocationSndr': S.LOCATION_SNDR, 'StreetSndr': S.STREET_SNDR, 'HouseSndr': S.HOUSE_SNDR,
                            'LetterSndr': S.LETTER_SNDR, 'SlashSndr': S.SLASH_SNDR, 'CorpusSndr': S.CORPUS_SNDR,
                            'BuildingSndr': S.BUILDING_SNDR, 'HotelSndr': S.HOTEL_SNDR, 'RoomSndr': S.ROOM_SNDR}

        # Summary
        # Поля секции: Summary
        self.summary_fields = ['MailCount', 'MailWeight', 'ValueSum', 'DeliveryRateSum', 'DeliveryRateVAT',
                               'DeliveryRateTotal', 'ValueSumRateTotal', 'ValueSumRateVAT', 'NoticeRateTotal',
                               'NoticeRateVAT', 'SMSNoticeTotal', 'SMSNoticeVAT', 'TotalRate', 'TotalRateVAT']
        # Словарь секции: Summary
        self.summary_dict = {'MailCount': self._list_rpo.rpo_count, 'MailWeight': 0, 'ValueSum': 0,
                             'DeliveryRateSum': self.mass_rate, 'DeliveryRateVAT': self.nds_mass_rate,
                             'DeliveryRateTotal': self.sum_mass_rate, 'ValueSumRateTotal': 0, 'ValueSumRateVAT': 0,
                             'NoticeRateTotal': 0, 'NoticeRateVAT': 0, 'SMSNoticeTotal': 0, 'SMSNoticeVAT': 0,
                             'TotalRate': self.sum_mass_rate, 'TotalRateVAT': self.nds_mass_rate}

        # DOCVERSION
        # Поля секции: DocVersion
        self.docversion_fields = ['DocVersion']
        # Словарь секции: DocVersion
        self.docversion_dict = {'DocVersion': self.version}

        # Заголовок TXT файла
        self.header = ['Barcode', 'Mass', 'MassRate', 'Payment', 'Value', 'InsrRate', 'AirRate', 'Rcpn',
                       'AddressTypeTo', 'NumAddressTypeTo', 'IndexTo', 'RegionTo', 'AreaTo', 'PlaceTo', 'LocationTo',
                       'StreetTo', 'HouseTo', 'LetterTo', 'SlashTo', 'CorpusTo', 'BuildingTo', 'HotelTo', 'RoomTo',
                       'Comment', 'MailDirect', 'TelAddress', 'Length', 'Width', 'Height', 'VolumeWeight',
                       'SMSNoticeR', 'MPODeclaration', 'PaymentCurrency']

        # Формат строки TXT файла
        self.f = '{barcode}|{mass}|{mass_rate}|0|0|0|0|{reception}|1||{index}|||||' \
                 '{address}|||||||||643||0|0|0|0|||RUB\n'

        # Заголовок TXT файла в строку
        self.header_string = '|'.join(self.header)

    # Возвращает название файла
    def get_file_name(self):
        y = str(self._list_rpo.date.year)[-1]
        start_date = date(self._list_rpo.date.year, 1, 1)
        days = '%03d' % ((self._list_rpo.date - start_date).days + 1)
        inn = '%012d' % int(S.INN)
        list_num = '%05d' % self._list_rpo.num
        return '{}{}{}{}'.format(inn, y, days, list_num)

    # Заполняет конфиг данными
    def create_config(self):
        cfg = ConfigParser()
        cfg.optionxform=str
        # Секция: Main
        cfg.add_section('Main')
        for f in self.main_fields:
            cfg.set('Main', f, str(self.main_dict[f]))

        # Секция: Sender
        cfg.add_section('Sender')
        for f in self.sender_fields:
            cfg.set('Sender', f, str(self.sender_dict[f]))

        # Секция: Summary
        cfg.add_section('Summary')
        for f in self.summary_fields:
            cfg.set('Summary', f, str(self.summary_dict[f]))

        # Секция: DocVersion
        cfg.add_section('DocVersion')
        for f in self.docversion_fields:
            cfg.set('DocVersion', f, str(self.docversion_dict[f]))

        return cfg

    # Создает TXT файл
    def create_txt(self, path_to_dir):
        """
        :param path_to_dir: Путь к папке сохранения
        :return: Путь до сохраненного файла
        """
        name = '{}.txt'.format(self.get_file_name())
        file_path = os.path.join(path_to_dir, name)
        if self._list_rpo.rpo_count > 0:
            with open(file_path, 'w', encoding='cp866') as save_file:
                save_file.write('{}\n'.format(self.header_string))
                rpos = session.query(Rpo).join(ListRpo).filter(ListRpo.id == self._list_rpo.id).order_by(Rpo.num_string).all()
                for rpo in rpos:
                    line = self.f.format(barcode=rpo.barcode, mass=rpo.mass,
                                         mass_rate=self.format_int(rpo.mass_rate, True), reception=rpo.reception,
                                         address=rpo.address, index=rpo.index)
                    save_file.write(line)
            return file_path
        return False

    # Создает INI файл
    def create_ini(self, path_to_dir):
        """
        :param path_to_dir: Путь к папке сохранения
        :return: Путь до сохраненного файла
        """
        name = '{}h.ini'.format(self.get_file_name())
        file_path = os.path.join(path_to_dir, name)
        cfg = self.create_config()
        with open(file_path, 'w', encoding='cp866') as save_file:
            cfg.write(save_file)
        return file_path

    # Сохраняет файлы
    def save(self, path_to_dir):
        """
        :param path_to_dir: Путь к папке сохранения
        :return: [Путь до файла TXT, Путь до файла INI]
        """
        path_txt = self.create_txt(path_to_dir)
        #path_txt = 'Test'
        path_ini = self.create_ini(path_to_dir)
        return [path_txt, path_ini]

    # Форматирует float в int
    @staticmethod
    def format_int(float_num, nds=False):
        """
        :param float_num: Число в формате float
        :param nds: Прибавлять nds
        :return: Число в формате int
        """
        if type(float_num) in (float, int):
            if not nds:
                return int(float_num * 100)
            else:
                return int(round(float_num * 1.18 * 100))
        return 0
