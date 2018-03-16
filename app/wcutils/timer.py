#!/usr/bin/env python
# -*- coding: utf-8 -*-


import timeit


__author__ = 'WorldCount'


"""
Утилиты для измерения скорости выполнения
"""


# Менеджер контекста: время выполнения
class Timer:

    def __init__(self, verbose=True):
        self.verbose = verbose
        self.start = None
        self.end = None
        self.secs = None

    def __enter__(self):
        self.start = timeit.default_timer()
        return self

    def __exit__(self, *args):
        self.end = timeit.default_timer()
        self.secs = self.end - self.start

        if self.verbose:
            print(self.format_time())

    def format_time(self):
        h = self.secs // 3600
        m = (self.secs // 60) % 60
        s = self.secs % 60
        result = 'Затраченное время: {0:02}:{1:02}:{2:02}'.format(int(h), int(m), int(s))
        return result


# Декоратор для измерения скорости выполнения
def get_time_exec(func):
    def wrapper():
        with Timer(True):
            return func()
    return wrapper
