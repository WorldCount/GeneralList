#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt5.QtCore import (QThread, pyqtSignal)
from app.gen_files import GenFileReader
from app.post_data.rtm import GenRTMFormat
from app.models import ListRpo
from app import session


__author__ = 'WorldCount'


class DeleteThread(QThread):

    current_progress = pyqtSignal(int, int)

    def __init__(self, data_list: list, size: int, parent=None):
        super(DeleteThread, self).__init__(parent)
        self.data_list = data_list
        self.size = size

    def run(self):
        self.current_progress.emit(0, self.size)
        for num, data in enumerate(self.data_list):
            current_session = session.object_session(data)
            current_session.delete(data)
            current_session.commit()
            self.current_progress.emit(num + 1, self.size)


class SaveFileThread(QThread):
    current_progress = pyqtSignal(int, int)

    def __init__(self, files, size, path, parent=None):
        super(SaveFileThread, self).__init__(parent)
        self.path = path
        self.files = files
        self.size = size

    def run(self):
        self.current_progress.emit(0, self.size)
        for num, file in enumerate(self.files):
            self.work_with_file(file)
            self.current_progress.emit(num + 1, self.size)

    def work_with_file(self, file):
        rtm = GenRTMFormat(file)
        rtm.save(self.path)


class LoadFileThread(QThread):
    add_file = pyqtSignal(int, ListRpo, int, str)
    save_data = pyqtSignal()

    def __init__(self, files, size: int, date, parent=None):
        super(LoadFileThread, self).__init__(parent)
        self.files = files
        self.size = size
        self.date = date

    def run(self):
        for num, file in enumerate(self.files):
            self.work_with_file(num, file)
        self.save_data.emit()
        session.commit()

    def work_with_file(self, num, file):
        parser = GenFileReader(file, list_date=self.date, find_error=True)
        reader = parser.parse()
        list_rpo = ListRpo.query.order_by(ListRpo.id.desc()).first()
        self.add_file.emit(num, list_rpo, self.size, parser.ext)
