#!/usr/bin/env python
# -*- coding: utf-8 -*-


import socket
import subprocess
import urllib.request


__author__ = 'WorldCount'


"""
Утилиты для работы с сетью
"""


# Возвращает IP-адрес компьютера
def get_ip_address():
    """
    :return: ИП-адресс компьютера
    """
    return socket.gethostbyname(socket.gethostname())


# Возвращает внешний IP-адрес компьютера
def get_ext_ip_address():
    """
    :return: Внешний ИП-адресс компьютера или False
    """
    url = 'http://icanhazip.com'
    res = urllib.request.urlopen(url)
    data = res.read()
    return data.decode().strip() or False


# Возвращает имя компьютера
def get_host_name():
    """
    :return: Хост компьютера
    """
    return socket.gethostname()


# Возвращает статус сервера или сайта
def ping(ip, num=1, wait=1):
    """
    :param ip: ИП-адрес
    :param num: Количество пакетов
    :param wait: Время ожидания ответа
    :return: Статус соединения
    """
    pipe = subprocess.Popen(['ping', '-n', str(num), '-w', str(wait), ip],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    response = pipe.communicate()[0].decode('cp866')
    if 'TTL' in response:
        return True
    return False
