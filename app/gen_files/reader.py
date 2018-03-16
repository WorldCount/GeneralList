#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'WorldCount'


class Reader:

    def __init__(self, link):
        self._link = link

    def _init_header(self):
        pass

    def _read_data(self):
        pass

    def load(self):
        pass

    @property
    def link(self):
        return self._link