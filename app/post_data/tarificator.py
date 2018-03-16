#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'WorldCount'


# Вид отправлений
class MailTypes:
    UNDEF = 0
    MAIL = 2
    PARCEL = 3
    AUTO = 99


# Словарь типов
MailTypes_Dict = {MailTypes.UNDEF: 'Неизв.', MailTypes.MAIL: 'Письмо',
                  MailTypes.PARCEL: 'Бандероль', MailTypes.AUTO: 'Авто'}
# Словарь типов
MailTypes_Dict_Desc = {'Неизв.': MailTypes.UNDEF,  'Письмо': MailTypes.MAIL, 'Бандероль': MailTypes.PARCEL}


class ConfigTarificator:
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


# Тарификатор отправлений
class Tarificator:

    def __init__(self, config=ConfigTarificator):
        self._config = config

    # Округляет вес до шага
    def round_weight(self, weight_in_grams):
        """
        :param weight_in_grams: Вес в граммах
        :return: Округленный вес
        """
        if not weight_in_grams: weight_in_grams = 0

        weight_step = self._config.WEIGHT_STEP

        if weight_in_grams % weight_step == 0:
            return weight_in_grams
        return weight_step - (weight_in_grams % weight_step) + weight_in_grams

    # Тарифицирует отправление
    def get_mass_rate(self, weight_in_grams, types=MailTypes.MAIL, nds=False, return_type=float):
        """
        :param weight_in_grams: Вес в граммах
        :param types: Вид отправления
        :param nds: Прибавить НДС
        :param return_type: Возвращаемый тип
        :return: Тариф на пересылку отправления
        """
        round_weight = self.round_weight(weight_in_grams)
        mass_rate = 0

        # Письмо
        if (types == MailTypes.MAIL) and (round_weight <= self._config.END_MAIL_WEIGHT):
            if round_weight > 0:
                calculate_weight = round_weight - self._config.START_MAIL_WEIGHT
                step = calculate_weight / self._config.WEIGHT_STEP
                mass_rate = self._config.START_MAIL_TARIF + (step * self._config.PAY_PER_STEP)
        # Бандероль
        elif (types == MailTypes.PARCEL) and (round_weight >= self._config.START_PARCEL_WEIGTH):
            if round_weight <= self._config.END_PARCEL_WEIGHT:
                calculate_weight = round_weight - self._config.START_PARCEL_WEIGTH
                step = calculate_weight / self._config.WEIGHT_STEP
                mass_rate = self._config.START_PARCEL_TARIF + (step * self._config.PAY_PER_STEP)
        # Авто
        elif (types == MailTypes.AUTO) and (round_weight > 0) and (round_weight <= self._config.END_PARCEL_WEIGHT):
            if round_weight <= 100:
                calculate_weight = round_weight - self._config.START_MAIL_WEIGHT
                step = calculate_weight / self._config.WEIGHT_STEP
                mass_rate = self._config.START_MAIL_TARIF + (step * self._config.PAY_PER_STEP)
            else:
                calculate_weight = round_weight - self._config.START_PARCEL_WEIGTH
                step = calculate_weight / self._config.WEIGHT_STEP
                mass_rate = self._config.START_PARCEL_TARIF + (step * self._config.PAY_PER_STEP)

        if nds:
            mass_rate = round(mass_rate * 1.18, 2)

        if return_type == float:
            return float(mass_rate)
        elif return_type == int:
            return int(mass_rate * 100)
        elif return_type == str:
            return str(int(mass_rate * 100))
        return mass_rate

    # Возвращает вид отправления
    def check_type(self, weight_in_grams, mass_rate, nds=False):
        """
        :param weight_in_grams: Вес в граммах
        :param mass_rate: Плата за отправку
        :param nds: Плата с НДС
        :return: Вид отправления
        """
        start_parcel_tarif = self._config.START_PARCEL_TARIF if not nds else self._config.START_PARCEL_TARIF * 1.18

        if (weight_in_grams >= self._config.START_PARCEL_WEIGTH) and (mass_rate >= start_parcel_tarif):
            return MailTypes.PARCEL
        elif (weight_in_grams <= self._config.END_MAIL_WEIGHT) and \
                (mass_rate <= self.get_mass_rate(self._config.END_MAIL_WEIGHT, MailTypes.MAIL, nds=nds)):
            return MailTypes.MAIL
        else:
            return MailTypes.UNDEF

    # Преобразует данные из строки в int
    def string_to_num(self, string_value):
        res = None
        if type(string_value) == str:
            temp = string_value.replace(' ', '').replace(',', '.')
            try:
                res = int(temp)
                return res
            except ValueError:
                pass

            if res is None:
                try:
                    res = int(float(temp) * 1000)
                    return res
                except ValueError:
                    return False
        if type(string_value == float):
            if string_value > 1.0:
                return int(string_value)
            else:
                return int(string_value * 1000)
        if type(string_value == int):
            return string_value
        return False
