#!/usr/bin/env python
# -*- coding: utf-8 -*-


import hashlib


__author__ = 'WorldCount'


"""
Работа с хешем
"""


# Возвращает хеш-сумму пароля
def password_to_hash(password):
    """
    :param password: Строка с паролем
    :return: Хеш пароля
    """
    md5 = hashlib.md5(password.encode())
    return md5.hexdigest()
