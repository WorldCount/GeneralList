#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib.request
from urllib.parse import urlencode


__author__ = 'WorldCount'


"""
Работа с телеграмом
"""


TOKEN = '217628569:AAEsYJ_Yl1FJXgjUqZeIJ08zWgwwkHcC7YI'
API = 'https://api.telegram.org/bot{token}/sendMessage?{params}'
HTML_MODE = 'HTML'
MARKDOWN_MODE = 'Markdown'


# Отправляет сообщение в телеграмм
def send(message, chat_id, parse_mode=None, token=TOKEN):
    """
    :param message: Текст сообщения
    :param chat_id: ID чата
    :param parse_mode: Режим форматирования сообщения
    :param token: Токен бота
    :return: Статус отправки
    """
    params = {'chat_id': chat_id, 'text': message, 'parse_mode': parse_mode}
    url = API.format(token=token, params=urlencode(params))
    resp = urllib.request.urlopen(url)
    if resp.code != 200:
        return False
    return True
