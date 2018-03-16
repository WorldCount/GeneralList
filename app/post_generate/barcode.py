#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'WorldCount'


"""
Работа с контрольным разрядом
"""

__CONSTLIST = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# Множители
__MULTIPLIERS = [8, 6, 4, 2, 3, 5, 9, 7]


# Генерирует ШПИ полностью для любого отправления
def gen_barcode(barcode):
    value = str(barcode)
    value_len = len(value)

    if value_len < 13 or value_len > 14:
        return False

    if value[:1] in __CONSTLIST:
        return gen_numeric_barcode(value)
    else:
        return gen_ems_barcode(value)


# Возвращает ШПИ международного отправления
def gen_ems_barcode(barcode):
    # cумма элементов
    number_sum = 0

    value = str(barcode)
    value_len = len(value)

    if value_len != 13:
        return False

    # начало, конец и центр(без КР) ШПИ
    num_start = value[:2]
    num_end = value[-2:]
    num_value = value[2: -3]
    # ШПИ разбитый по цифрам
    list_value = list(num_value)

    try:
        for i, num in enumerate(list_value):
            number_sum += (int(num) * __MULTIPLIERS[i])
    except ValueError:
        return False

    num_kr = 11 - (number_sum % 11)

    if num_kr == 10:
        kr = '0'
    elif num_kr == 11:
        kr = '5'
    else:
        kr = str(num_kr)

    return '%s%s%s%s' % (num_start, num_value, kr, num_end)


# Возвращает ШПИ обыкновенного отправления
def gen_numeric_barcode(barcode):
    # Сумма четных
    even = 0
    # Сумма нечетных
    odd = 0

    value = str(barcode)
    value_len = len(value)

    if value_len < 13 or value_len > 14:
        return False

    for i, num in enumerate(value[0:13]):
        try:
            # если четное
            if i % 2 == 0:
                even += int(num)
            else:
                odd += int(num)
        except ValueError:
            return False
        i += 1

    even *= 3
    all_num = even + odd
    num_kr = 10 - (all_num % 10)

    if num_kr == 10:
        kr = '0'
    else:
        kr = str(num_kr)

    if value_len == 13:
        return '%s%s' % (value, kr)
    else:
        return '%s%s' % (value[:-1], kr)


# Генерирует только КР для любого отправления
def gen_control_rank(barcode):
    result = gen_barcode(barcode)

    if result:
        if result[:1] in __CONSTLIST:
            return result[-1:]
        else:
            return result[-3:-2]
    else:
        return False


# Гененерирует ШПИ
def create_barcode(ops_num, month_num, rpo_num):
    try:
        month = '%02d' % int(month_num)
        rpo = '%05d' % int(rpo_num)
        barcode = '%s%s%s' % (str(ops_num), month, rpo)
        return gen_barcode(barcode)
    except ValueError:
        return False


# Генерирует диапазон ШПИ
def create_barcode_list(ops_num, month_num, in_num, out_num):
    result = []

    try:
        ops = str(ops_num)
        if len(ops) < 6:
            return False

        for i in range(int(in_num), int(out_num) + 1):
            barcode = create_barcode(ops, month_num, i)
            if barcode:
                result.append(barcode)
        return result

    except ValueError:
        return False


# Парсит ШПИ
def parse_barcode(barcode):
    res = {'barcode': '', 'month': '', 'num': '', 'ops': '', 'controlrank': ''}
    try:
        barcode = str(barcode)
        barcode_len = len(barcode)
        if barcode_len != 14:
            return False

        res['barcode'] = barcode
        res['month'] = barcode[6:8]
        res['ops'] = barcode[:6]
        res['controlrank'] = barcode[-1]
        res['num'] = barcode[8:barcode_len - 1]
        return res
    except ValueError:
        return False


# Изменяет номер ШПИ на указанное число
def change_barcode(barcode, num):
    parse_bar = parse_barcode(barcode)
    if not parse_bar:
        return False

    try:
        barcode_num = int(parse_bar['num']) + int(num)
        if barcode_num > 99999 or barcode_num <= 0:
            return False
        return create_barcode(parse_bar['ops'], parse_bar['month'], barcode_num)
    except ValueError:
        return False


# Повышает номер ШПИ на указанное число
def increment_barcode(barcode, num=1):
    try:
        inc_num = int(num)
        if num < 0:
            inc_num *= -1
        return change_barcode(barcode, inc_num)
    except ValueError:
        return False


# Понижает ШПИ на указанное число
def decrement_barcode(barcode, num=1):
    try:
        dec_num = int(num)
        if num > 0:
            dec_num *= -1
        return change_barcode(barcode, dec_num)
    except ValueError:
        return False
