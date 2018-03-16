# -*- coding: utf-8 -*-

import os
from datetime import date
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QSpinBox, QCalendarWidget, QComboBox, QDateEdit,
                             QGridLayout, QCheckBox, QTableWidget, QAbstractItemView, QAction, QHeaderView, QMessageBox, QTableWidgetItem,
                             QCompleter, QLineEdit, QProgressBar, QFileDialog)
from PyQt5.QtGui import (QIcon, QRegExpValidator, QColor, QPixmap)
from PyQt5.QtCore import (Qt, QRegExp, pyqtSignal, QModelIndex, QTimer, QStringListModel, QSize)

from app import session
from app.models import (ListRpo, Rpo, Index, Completion, Config)
from app.wcutils.date import format_date
from app.wcutils.files import (find_files, create_dirs)
from app.post_generate.barcode import gen_control_rank
from app.post_data.tarificator import (Tarificator, MailTypes_Dict, MailTypes_Dict_Desc, MailTypes)
from app.interface.widgets import (EditWidget, UpperCaseValidator, ButtonWidget, HLine)
from app.interface.threads import (SaveFileThread, LoadFileThread, DeleteThread)
from config import (TarificatorConfig, AppConfig)

__author__ = 'WorldCount'


TYPE_LIST_KEY = sorted(MailTypes_Dict_Desc.keys())

M_TYPE = {'Письмо': 2, 'Бандероль': 3}
M_TYPE_KEYS = sorted(M_TYPE.keys())


# Таблица с загруженными файлами
class FilesTableWidget(QTableWidget):

    def __init__(self, *args):
        super(FilesTableWidget, self).__init__(*args)
        self._root = os.path.dirname(__file__)
        self.header = self.horizontalHeader()
        self.header_list = []

        self.excel_ico = QPixmap(os.path.join(self._root, 'icon', 'excel.png'))
        self.dbf_ico = QPixmap(os.path.join(self._root, 'icon', 'dbf.png'))
        self.no_ico = QPixmap(os.path.join(self._root, 'icon', 'no_ext.png'))

        self.configure()

    def configure(self):
        self.setRowCount(0)
        self.header.setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSortingEnabled(False)

        self.excel_ico = self.excel_ico.scaled(QSize(28, 28), Qt.KeepAspectRatio)
        self.dbf_ico = self.dbf_ico.scaled(QSize(28, 28), Qt.KeepAspectRatio)
        self.no_ico = self.no_ico.scaled(QSize(28, 28), Qt.KeepAspectRatio)

    def setHorizontalHeaderLabels(self, header_list, p_str=None):
        self.header_list = header_list
        super(FilesTableWidget, self).setHorizontalHeaderLabels(header_list)
        self.header_resize()

    def header_resize(self):
        last_col = len(self.header_list) - 1
        for num, col in enumerate(self.header_list):
            if num == last_col:
                self.header.setSectionResizeMode(num, QHeaderView.Stretch)
            else:
                self.header.setSectionResizeMode(num, QHeaderView.ResizeToContents)

    def add_row(self, row_num, list_rpo: ListRpo, ext: str= 'dbf', colorize=False, insert=True):

        if ext == '':
            icon = self.no_ico
        elif ext == 'dbf':
            icon = self.dbf_ico
        else:
            icon = self.excel_ico

        icon_item = QLabel()
        icon_item.setPixmap(icon)

        num = QTableWidgetItem(self.value_format(list_rpo.num))
        mail_type = QTableWidgetItem(self.value_format(MailTypes_Dict.get(list_rpo.mail_type, 'Неизв.')))
        count = QTableWidgetItem(self.value_format(list_rpo.rpo_count))
        error = QTableWidgetItem(self.value_format(list_rpo.error_count))
        double = QTableWidgetItem(self.value_format(list_rpo.double_count))
        mass_rate = QTableWidgetItem(' %.2f ' % list_rpo.mass_rate)
        author = QTableWidgetItem(self.value_format(list_rpo.author))

        icon_item.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        num.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        mail_type.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        count.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        error.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        double.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        mass_rate.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        if insert:
            self.insertRow(row_num)

        self.setCellWidget(row_num, 0, icon_item)
        self.setItem(row_num, 1, num)
        self.setItem(row_num, 2, count)
        self.setItem(row_num, 3, error)
        self.setItem(row_num, 4, double)
        self.setItem(row_num, 5, mass_rate)
        self.setItem(row_num, 6, author)

        if colorize:
            color = QColor('#FFF')
            if list_rpo.double_count == 0 and list_rpo.error_count == 0: color = QColor('#D5F5E3')
            if list_rpo.error_count > 0: color = QColor('#FAD7A0')
            if list_rpo.double_count > 0: color = QColor('#FFC0CB')
            for num, text in enumerate(self.header_list):
                self.set_cell_color(row_num, num, color)

    def value_format(self, value):
        return ' {} '.format(value)

    # Метод: закрашивает ячейку таблицы
    def set_cell_color(self, row, col, color):
        item = self.item(row, col)
        if item:
            item.setBackground(color)


# Таблица с индексами
class IndexTableWidget(QTableWidget):

    double_click = pyqtSignal(str)
    enter_completed = pyqtSignal(str)

    def __init__(self, *args):
        super(IndexTableWidget, self).__init__(*args)
        self._root = os.path.dirname(__file__)
        self.header = self.horizontalHeader()
        self.header_list = []

        self.configure()

    def configure(self):
        self.setRowCount(0)
        self.verticalHeader().setVisible(False)
        self.setColumnWidth(1, 260)
        self.header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.header.setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSortingEnabled(False)

    def setHorizontalHeaderLabels(self, header_list, p_str=None):
        self.header_list = header_list
        super(IndexTableWidget, self).setHorizontalHeaderLabels(header_list)

    def header_resize(self):
        last_col = len(self.header_list) - 1
        for num, col in enumerate(self.header_list):
            if num == last_col:
                self.header.setSectionResizeMode(num, QHeaderView.Stretch)
            else:
                self.header.setSectionResizeMode(num, QHeaderView.ResizeToContents)

    def set_double_click(self, func):
        self.double_click.connect(func)

    def add_row(self, row_num, index: Index, insert=True):
        index_num = QTableWidgetItem(self.value_format(index.index))
        city = QTableWidgetItem(self.value_format(index.name))
        region = QTableWidgetItem(self.value_format(index.region))

        if insert:
            self.insertRow(row_num)

        self.setItem(row_num, 0, index_num)
        self.setItem(row_num, 1, city)
        self.setItem(row_num, 2, region)

    def value_format(self, value):
        return ' {} '.format(value)

    # Метод: возвращает индекс
    def get_index(self, index: QModelIndex):
        item = self.item(index.row(), 0)
        if item:
            return item.text()
        return False

    def keyPressEvent(self, event):
        if event.key() in (16777221, 16777220):
            index = self.currentIndex()
            select_index = self.get_index(index)
            if select_index:
                self.enter_completed.emit(str(select_index).strip())
                event.accept()
        return QTableWidget.keyPressEvent(self, event)


# Таблица с РПО
class RpoTableWidget(QTableWidget):

    double_click = pyqtSignal(str)
    delete_row = pyqtSignal()

    def __init__(self, *args):
        super(RpoTableWidget, self).__init__(*args)
        self._root = os.path.dirname(__file__)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.header = self.horizontalHeader()
        self.header_list = []
        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH

        self.configure()
        self.init_action()

    def configure(self):
        self.setRowCount(0)
        self.setColumnWidth(7, 10)
        self.header.setSectionResizeMode(7, QHeaderView.Fixed)
        self.header.setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSortingEnabled(False)
        self.doubleClicked.connect(self.emit_rid)

    def init_action(self):
        separator1 = QAction('', self)
        separator1.setSeparator(True)
        separator2 = QAction('', self)
        separator2.setSeparator(True)

        delete_rpo = QAction(QIcon(os.path.join(self._root, 'icon', 'delete.png')), 'Удалить рпо', self)
        delete_rpo.triggered.connect(self.delete_rpo)

        self.addAction(separator1)
        self.addAction(delete_rpo)
        self.addAction(separator2)

    def setHorizontalHeaderLabels(self, header_list, p_str=None):
        self.header_list = header_list
        super(RpoTableWidget, self).setHorizontalHeaderLabels(header_list)
        self.header_resize()

    def header_resize(self):
        last_col = len(self.header_list) - 2
        for num, col in enumerate(self.header_list):
            if num == last_col:
                self.header.setSectionResizeMode(num, QHeaderView.Stretch)
            else:
                self.header.setSectionResizeMode(num, QHeaderView.ResizeToContents)

    def set_double_click(self, func):
        self.double_click.connect(func)

    def add_row(self, row_num, rpo: Rpo, colorize=False, insert=True):
        rid = QTableWidgetItem(self.value_format(str(rpo.id)))
        num = QTableWidgetItem(self.value_format(str(rpo.num_string)))
        barcode = QTableWidgetItem(self.value_format(str(rpo.barcode)))
        mass = QTableWidgetItem(self.value_format(str(rpo.mass)))
        mass_rate = QTableWidgetItem(self.value_format('%.2f' % rpo.mass_rate))
        error = QTableWidgetItem(self.value_format(str(rpo.error_count)))
        index = QTableWidgetItem(self.value_format(str(rpo.index)))
        reception = QTableWidgetItem(self.value_format(str(rpo.reception)))
        address = QTableWidgetItem(self.value_format(str(rpo.address)))

        num.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        barcode.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        mass.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        mass_rate.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        error.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        index.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        if insert:
            self.insertRow(row_num)

        self.setItem(row_num, 0, rid)
        self.setItem(row_num, 1, num)
        self.setItem(row_num, 2, barcode)
        self.setItem(row_num, 3, mass)
        self.setItem(row_num, 4, mass_rate)
        self.setItem(row_num, 5, error)
        self.setItem(row_num, 6, index)
        self.setItem(row_num, 7, reception)
        self.setItem(row_num, 8, address)

        if colorize:
            color = QColor('#FFF')
            if rpo.error_count == 0:
                color = QColor('#D5F5E3')
            else:
                color = QColor('#FFC0CB')

            for num, text in enumerate(self.header_list):
                self.set_cell_color(row_num, num, color)

    def delete_rpo(self):
        ind = self.currentIndex()
        ind_row = ind.row()
        rpo = self.get_rpo_by_index(ind)
        if rpo:
            msg = self.create_mgs_box(rpo)
            btn_y = msg.button(QMessageBox.Yes)
            msg.exec_()
            if msg.clickedButton() == btn_y:
                session.delete(rpo)
                session.commit()
                self.removeRow(ind_row)
                self.delete_row.emit()

    # Метод: возвращает id РПО по индексу
    def get_id_by_index(self, index: QModelIndex):
        item = self.item(index.row(), 0)
        if item:
            return item.text()
        return False

    def get_rpo_by_index(self, index):
        rid = self.get_id_by_index(index)
        if rid:
            return Rpo.query.get(rid)
        return None

    # Метод: закрашивает ячейку таблицы
    def set_cell_color(self, row, col, color):
        item = self.item(row, col)
        if item:
            item.setBackground(color)

    def create_mgs_box(self, rpo: Rpo):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle('Удаление РПО')
        txt = 'Вы действительно хотите удалить РПО:\n№: {}, ШПИ: {}, Вес: {}?'
        msg.setText(txt.format(rpo.num_string, rpo.barcode, rpo.mass))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        btn_y = msg.button(QMessageBox.Yes)
        btn_y.setText('Да')
        btn_n = msg.button(QMessageBox.No)
        btn_n.setText('Нет')
        msg.setDefaultButton(QMessageBox.No)
        return msg

    def emit_rid(self, index: QModelIndex):
        rid = self.get_id_by_index(index)
        if rid:
            self.double_click.emit(rid)

    def value_format(self, value):
        return ' {} '.format(value)


# Диалог удаления файлов
class DeleteFilesDialog(QDialog):

    font = AppConfig.FONT

    def __init__(self, ids: list, parent=None):
        super(DeleteFilesDialog, self).__init__(parent)
        self.parent = parent
        self._root = os.path.dirname(__file__)
        self.ids = ids
        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH
        self.progress = QProgressBar()
        # Поток для удаления файлов
        self.delete_thread = None

        self.init_ui()
        self.init_widget()
        self.init_connect()

    def init_ui(self):
        self.setWindowTitle('Удаление списков')
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setMinimumSize(400, 100)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
                            Qt.WindowStaysOnTopHint | Qt.WindowMaximizeButtonHint)

    def init_widget(self):
        vbox = QVBoxLayout()

        label = QLabel('Удаление списков:')
        label.setFont(self.font)
        self.progress.setFixedHeight(self.widget_height)
        self.progress.setTextVisible(True)
        vbox.addWidget(label)
        vbox.addWidget(self.progress)
        vbox.addStretch(1)
        self.setLayout(vbox)

        #rpo_lists = ListRpo.query.filter(ListRpo.id.in_(self.ids)).all()
        rpo_lists = session.query(ListRpo).filter(ListRpo.id.in_(self.ids)).all()
        size = len(rpo_lists)
        if size > 0:
            self.progress.setMaximum(size)
            self.delete_thread = DeleteThread(rpo_lists, size, self)
            self.delete_thread.current_progress.connect(self.progress_worked)
            self.delete_thread.finished.connect(self.save_finished)
            self.delete_thread.start()
        else:
            self.progress.setMaximum(1)
            self.progress.setValue(1)
            self.progress.setFormat('Нет списков для удаления!')

    def init_connect(self):
        pass

    def save_finished(self):
        self.progress.setFormat('Готово!')
        self.accept()

    def progress_worked(self, num: int, size: int):
        self.progress.setValue(num)
        self.progress.setFormat('Файл {} из {}'.format(num, size))

    def closeEvent(self, event):
        if self.delete_thread and self.delete_thread.isRunning():
            event.ignore()


# Диалог загрузки файлов
class LoadFilesDialog(QDialog):

    font = AppConfig.FONT

    def __init__(self, path=None, parent=None):
        super(LoadFilesDialog, self).__init__(parent)
        self.parent = parent
        self._root = os.path.dirname(__file__)
        self._path = path
        self.header = ['Тип', 'Номер', 'Кол-во', 'Ошибок', 'Дублей', 'Плата', 'Автор']
        # Раскрашивать строки
        self.colorize = AppConfig.COLORIZE
        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH
        # Виджеты
        self.table = FilesTableWidget(1, len(self.header))
        self.list_date = QDateEdit(date.today())
        self.path_line = QLineEdit()
        self.btn_choose = QPushButton('Обзор')
        self.btn_load = QPushButton('Загрузить')
        self.btn_ok = QPushButton('Принять')
        self.progress = QProgressBar()
        # Поток для загрузки файлов
        self.load_thread = None

        self.init_ui()
        self.init_widget()
        self.init_connect()

    def init_ui(self):
        self.setWindowTitle('Загрузка файлов')
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setMinimumSize(640, 480)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
                            Qt.WindowStaysOnTopHint | Qt.WindowMaximizeButtonHint)

    def init_widget(self):
        self.table.setHorizontalHeaderLabels(self.header)
        self.table.setFont(self.font)

        vbox = QVBoxLayout()
        root_box = QHBoxLayout()
        root_box.setContentsMargins(0, 0, 0, 0)

        load_box = QHBoxLayout()
        load_box.setContentsMargins(0, 0, 0, 0)

        btn_box = QHBoxLayout()

        d_label = QLabel('Дата списков:')
        d_label.setFont(self.font)
        d_cal = QCalendarWidget()
        d_cal.setFirstDayOfWeek(Qt.Monday)
        d_cal.setGridVisible(True)
        d_cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.list_date.setFont(self.font)
        self.list_date.setFixedSize(130, self.widget_height)
        self.list_date.setCalendarPopup(True)
        self.list_date.setCalendarWidget(d_cal)

        label = QLabel('Путь к папке загрузки:')
        label.setFont(self.font)
        self.btn_choose.setFixedSize(self.button_width, self.widget_height)
        self.btn_choose.setFont(self.font)
        self.path_line.setFont(self.font)
        if self._path:
            self.path_line.setText(self._path)
        root_box.addWidget(self.path_line)
        root_box.addWidget(self.btn_choose)

        self.progress.setFixedHeight(self.widget_height)
        self.progress.setTextVisible(True)
        self.btn_load.setFixedSize(self.button_width, self.widget_height)
        self.btn_load.setFont(self.font)
        load_box.addWidget(self.progress)
        load_box.addWidget(self.btn_load)

        self.btn_ok.setFont(self.font)
        self.btn_ok.setFixedSize(self.button_width, self.widget_height)
        btn_box.addWidget(self.btn_ok)

        vbox.addWidget(d_label)
        vbox.addWidget(self.list_date)
        vbox.addWidget(label)
        vbox.addLayout(root_box)
        vbox.addLayout(load_box)
        vbox.addWidget(self.table)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

        self.btn_load.setFocus()

    def init_connect(self):
        self.btn_choose.clicked.connect(self.choose_dir)
        self.btn_load.clicked.connect(self.load_files)
        self.btn_ok.clicked.connect(self.submit_close)
        self.path_line.textChanged.connect(self.value_change)
        self.list_date.dateChanged.connect(self.value_change)

    def submit_close(self):
        self.accept()

    def choose_dir(self):
        load_dir = QFileDialog.getExistingDirectory(self, 'Выберите папку', self._path)
        if load_dir:
            self._path = load_dir
            Config.set_value('load_dir', self._path)
            self.path_line.setText(self._path)

    def load_files(self):
        self.button_enabled(False)
        create_dirs(self._path)
        self.progress.setValue(0)
        self.progress.setMaximum(0)
        self.progress.setFormat('')
        self.table.setRowCount(0)

        files = []
        for mask in AppConfig.FILE_MASKS:
            files.extend(find_files(self._path, mask))

        size = len(files)
        self.progress.setMaximum(size)

        if size > 0:
            self.load_thread = LoadFileThread(files, size, self.list_date.date().toPyDate(), self)
            self.load_thread.save_data.connect(self.save_data)
            self.load_thread.finished.connect(self.load_finished)
            self.load_thread.add_file.connect(self.add_file)
            self.load_thread.start()
        else:
            self.progress.setMaximum(1)
            self.progress.setValue(1)
            self.button_enabled(True)
            self.progress.setFormat('Нет файлов для загрузки!')

    def button_enabled(self, status: bool):
        self.btn_load.setEnabled(status)
        self.btn_ok.setEnabled(status)
        self.btn_choose.setEnabled(status)
        self.list_date.setEnabled(status)

    def save_data(self):
        self.progress.setFormat('Сохранение...')

    def load_finished(self):
        self.progress.setFormat('Готово!')
        self.button_enabled(True)
        self.btn_ok.setFocus()

    def add_file(self, num, list_rpo: ListRpo, size:int, ext: str):
        self.table.add_row(num, list_rpo, ext, self.colorize, insert=True)
        self.progress.setValue(num + 1)
        self.progress.setFormat('Файл {} из {}'.format(num + 1, size))

    def closeEvent(self, event):
        if self.load_thread and self.load_thread.isRunning():
            event.ignore()

    def value_change(self):
        self.btn_load.setFocus()


# Диалог сохранения файлов
class SaveFilesDialog(QDialog):

    font = AppConfig.FONT

    def __init__(self, ids: list, path=None, parent=None):
        super(SaveFilesDialog, self).__init__(parent)
        self.parent = parent
        self._root = os.path.dirname(__file__)
        self._path = path
        self.ids = ids
        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH
        # Поток для сохранения файлов
        self.save_thread = None
        # Виджеты
        self.path_line = QLineEdit()
        self.btn_choose = QPushButton('Обзор')
        self.btn_save = QPushButton('Сохранить')
        self.btn_ok = QPushButton('Принять')
        self.progress = QProgressBar()

        self.init_ui()
        self.init_widget()
        self.init_connect()

    def init_ui(self):
        self.setWindowTitle('Соранение файлов')
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setMinimumSize(640, 160)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
                            Qt.WindowStaysOnTopHint | Qt.WindowMaximizeButtonHint)

    def init_widget(self):
        vbox = QVBoxLayout()
        root_box = QHBoxLayout()
        root_box.setContentsMargins(0, 0, 0, 0)

        save_box = QHBoxLayout()
        save_box.setContentsMargins(0, 0, 0, 0)

        btn_box = QHBoxLayout()
        btn_box.setContentsMargins(0, 0, 110, 0)

        label = QLabel('Путь к папке сохранения:')
        label.setFont(self.font)
        self.btn_choose.setFixedSize(self.button_width, self.widget_height)
        self.btn_choose.setFont(self.font)
        self.path_line.setFont(self.font)
        if self._path:
            self.path_line.setText(self._path)
        root_box.addWidget(self.path_line)
        root_box.addWidget(self.btn_choose)

        self.progress.setFixedHeight(self.widget_height)
        self.progress.setTextVisible(True)
        self.btn_save.setFixedSize(self.button_width, self.widget_height)
        self.btn_save.setFont(self.font)
        save_box.addWidget(self.progress)
        save_box.addWidget(self.btn_save)

        self.btn_ok.setFont(self.font)
        self.btn_ok.setFixedSize(self.button_width, self.widget_height)
        btn_box.addWidget(self.btn_ok)

        vbox.addWidget(label)
        vbox.addLayout(root_box)
        vbox.addLayout(save_box)
        vbox.addLayout(btn_box)
        vbox.addStretch(1)
        self.setLayout(vbox)
        self.btn_save.setFocus()

    def init_connect(self):
        self.btn_choose.clicked.connect(self.choose_dir)
        self.btn_save.clicked.connect(self.save_files)
        self.btn_ok.clicked.connect(self.submit_close)
        self.path_line.textChanged.connect(self.value_change)

    def submit_close(self):
        self.accept()

    def choose_dir(self):
        save_dir = QFileDialog.getExistingDirectory(self, 'Выберите папку', self._path)
        if save_dir:
            self._path = save_dir
            Config.set_value('save_dir', self._path)
            self.path_line.setText(self._path)

    def save_files(self):
        self.button_enabled(False)

        create_dirs(self._path)
        self.progress.setValue(0)
        self.progress.setMaximum(0)
        self.progress.setFormat('Готово')

        files = ListRpo.query.filter(ListRpo.id.in_(self.ids)).all()
        size = len(files)
        self.progress.setMaximum(size)

        if size > 0:
            self.save_thread = SaveFileThread(files, size, self._path, self)
            self.save_thread.current_progress.connect(self.progress_worked)
            self.save_thread.finished.connect(self.save_finished)
            self.save_thread.start()
        else:
            self.progress.setMaximum(1)
            self.progress.setValue(1)
            self.button_enabled(True)
            self.progress.setFormat('Нет файлов для сохранения!')

    def progress_worked(self, num: int, size: int):
        self.progress.setValue(num)
        self.progress.setFormat('Файл {} из {}'.format(num, size))

    def save_finished(self):
        self.progress.setFormat('Готово!')
        self.button_enabled(True)
        self.btn_ok.setFocus()

    def closeEvent(self, event):
        if self.save_thread and self.save_thread.isRunning():
            event.ignore()

    def button_enabled(self, status: bool):
        self.btn_save.setEnabled(status)
        self.btn_ok.setEnabled(status)
        self.btn_choose.setEnabled(status)

    def value_change(self):
        self.btn_save.setFocus()


# Диалог выбора найденного индекса
class IndexSelectDialog(QDialog):

    font = AppConfig.FONT
    value = None

    def __init__(self, index_list: list, index: str=None, parent=None):
        super(IndexSelectDialog, self).__init__(parent)
        self.parent = parent
        self._root = os.path.dirname(__file__)
        self.index_list = index_list
        self.index = index

        self.header = ['Индекс', 'Город', 'Регион']

        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH

        self.table = IndexTableWidget(1, len(self.header))
        self.btn_ok = QPushButton('Принять')
        self.btn_cancel = QPushButton('Отмена')

        self.init_ui()
        self.init_widget()
        self.init_connect()

    def init_ui(self):
        self.setWindowTitle('Найденные индексы')
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setMinimumSize(640, 480)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
                            Qt.WindowStaysOnTopHint | Qt.WindowMaximizeButtonHint)

    def init_widget(self):
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 5, 0, 5)

        self.table.setHorizontalHeaderLabels(self.header)
        self.table.setFont(self.font)

        self.btn_ok.setFont(self.font)
        self.btn_ok.setFixedSize(self.button_width, self.widget_height)

        self.btn_cancel.setFont(self.font)
        self.btn_cancel.setFixedSize(self.button_width, self.widget_height)

        vbox.addWidget(self.table)

        self.setLayout(vbox)

        self.table.enter_completed.connect(self.table_enter)
        for num, index in enumerate(self.index_list):
            self.table.add_row(num, index)

        hbox.addWidget(self.btn_ok)
        hbox.addWidget(self.btn_cancel)
        vbox.addLayout(hbox)

        if self.index:
            ind = self.find_index(self.index[:4])
            self.table.selectRow(ind)
        else:
            self.table.selectRow(0)

    def init_connect(self):
        self.btn_cancel.clicked.connect(self.close)
        self.btn_ok.clicked.connect(self.submit_close)

    def find_index(self, text):
        ind = 0
        for num in range(self.table.rowCount()):
            item = self.table.item(num, 0)
            if item and text in item.text():
                ind = num
        return ind

    def table_enter(self, index):
        self.value = index
        self.accept()

    def submit_close(self):
        self.accept()

    def value_change(self):
        self.btn_ok.setFocus()


# Диалог редактирования номера списка
class NumListEditDialog(QDialog):
    value = None
    font = AppConfig.FONT

    def __init__(self, id_list, parent=None):
        super(NumListEditDialog, self).__init__(parent)
        self.id_list = id_list
        self.parent = parent
        self._root = os.path.dirname(__file__)
        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH
        # Виджеты
        self.number = QSpinBox()
        self.btn_ok = QPushButton('Принять')
        self.btn_cancel = QPushButton('Отмена')

        self.init_ui()
        self.init_widget()
        self.init_connect()

    # Инициализация: настройки
    def init_ui(self):
        self.setWindowTitle('Номер списка')
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    # Инициализация: виджеты
    def init_widget(self):
        hbox_btn = QHBoxLayout()
        hbox_btn.setContentsMargins(0, 20, 0, 0)
        vbox = QVBoxLayout()

        label = QLabel('Номер списка:')
        label.setFont(self.font)

        self.number.setFont(self.font)
        self.number.setFixedSize(240, 30)
        self.number.setMaximum(999999)
        self.number.setMinimum(1)
        self.number.setValue(self.id_list)

        self.btn_ok.setFont(self.font)
        self.btn_ok.setFixedSize(100, 30)

        self.btn_cancel.setFont(self.font)
        self.btn_cancel.setFixedSize(100, 30)

        hbox_btn.addWidget(self.btn_ok)
        hbox_btn.addWidget(self.btn_cancel)
        vbox.addWidget(label)
        vbox.addWidget(self.number)
        vbox.addLayout(hbox_btn)
        self.setLayout(vbox)
        self.btn_ok.setFocus()

    def init_connect(self):
        self.btn_ok.clicked.connect(self.submit_close)
        self.btn_cancel.clicked.connect(self.close)
        self.number.valueChanged.connect(self.value_change)

    def submit_close(self):
        self.value = int(self.number.value())
        self.accept()

    def value_change(self):
        self.btn_ok.setFocus()


# Диалог редактирования даты списка
class DateListEditDialog(QDialog):

    font = AppConfig.FONT
    value = None

    def __init__(self, date_list=None, parent=None):
        super(DateListEditDialog, self).__init__(parent)
        self.date_list = date_list or date.today()
        self.parent = parent
        self._root = os.path.dirname(__file__)

        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH

        # Виджеты
        self.calendar = QCalendarWidget()
        self.btn_ok = QPushButton('Принять')
        self.btn_cancel = QPushButton('Отмена')

        self.init_ui()
        self.init_widget()
        self.init_connect()

    def init_ui(self):
        self.setWindowTitle('Дата списка списка')
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def init_widget(self):
        vbox = QVBoxLayout()

        hbox_btn = QHBoxLayout()
        hbox_btn.setContentsMargins(0, 20, 0, 0)

        label = QLabel('Дата списка:')
        label.setFont(self.font)

        self.calendar.setSelectedDate(self.date_list)
        self.calendar.setMinimumWidth(300)
        self.calendar.setFont(self.font)

        self.btn_ok.setFont(self.font)
        self.btn_ok.setFixedSize(self.button_width, self.widget_height)

        self.btn_cancel.setFont(self.font)
        self.btn_cancel.setFixedSize(self.button_width, self.widget_height)

        hbox_btn.addWidget(self.btn_ok)
        hbox_btn.addWidget(self.btn_cancel)
        vbox.addWidget(label)
        vbox.addWidget(self.calendar)
        vbox.addLayout(hbox_btn)

        self.setLayout(vbox)

    def init_connect(self):
        self.btn_ok.clicked.connect(self.submit_close)
        self.btn_cancel.clicked.connect(self.close)

    def submit_close(self):
        self.value = self.calendar.selectedDate()
        self.accept()

    def value_change(self):
        self.btn_ok.setFocus()


# Диалог редактирования вида отправления
class MailTypeListEditDialog(QDialog):

    font = AppConfig.FONT
    value = None

    def __init__(self, mail_type=None, parent=None):
        super(MailTypeListEditDialog, self).__init__(parent)
        self.parent = parent
        self.mail_type = mail_type
        self._root = os.path.dirname(__file__)

        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH

        # Виджеты
        self.type_box = QComboBox()
        self.btn_ok = QPushButton('Принять')
        self.btn_cancel = QPushButton('Отмена')

        self.init_ui()
        self.init_widget()
        self.init_connect()

    def init_ui(self):
        self.setWindowTitle('Вид отправления')
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def init_widget(self):
        vbox = QVBoxLayout()
        hbox_btn = QHBoxLayout()
        hbox_btn.setContentsMargins(0, 20, 0, 0)

        label = QLabel('Вид отправления:')
        label.setFont(self.font)

        self.type_box.setFont(self.font)
        self.type_box.setFixedHeight(self.widget_height)
        self.type_box.addItems(TYPE_LIST_KEY)
        self.type_box.setCurrentIndex(TYPE_LIST_KEY.index(MailTypes_Dict.get(self.mail_type, 'Неизв.')))

        self.btn_ok.setFont(self.font)
        self.btn_ok.setFixedSize(self.button_width, self.widget_height)

        self.btn_cancel.setFont(self.font)
        self.btn_cancel.setFixedSize(self.button_width, self.widget_height)

        hbox_btn.addWidget(self.btn_ok)
        hbox_btn.addWidget(self.btn_cancel)
        vbox.addWidget(label)
        vbox.addWidget(self.type_box)
        vbox.addLayout(hbox_btn)
        self.setLayout(vbox)
        self.btn_ok.setFocus()

    def init_connect(self):
        self.btn_ok.clicked.connect(self.submit_close)
        self.btn_cancel.clicked.connect(self.close)
        self.type_box.currentIndexChanged.connect(self.value_change)

    def submit_close(self):
        self.value = MailTypes_Dict_Desc.get(self.type_box.currentText(), MailTypes.UNDEF)
        self.accept()

    def value_change(self):
        self.btn_ok.setFocus()


# Диалог создания списка РПО
class CreateListDialog(QDialog):

    font = AppConfig.FONT

    def __init__(self, parent=None):
        super(CreateListDialog, self).__init__(parent)
        self.parent = parent
        self._root = os.path.dirname(__file__)

        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH

        # Виджеты
        self.date_picker = QDateEdit(date.today())
        self.number = QSpinBox()
        self.type_box = QComboBox()
        self.btn_ok = QPushButton('Принять')
        self.btn_cancel = QPushButton('Отмена')

        # Настройки списка
        self.date = None
        self.num = None
        self.mail_type = None

        self.init_ui()
        self.init_widget()
        self.init_connect()

    def init_ui(self):
        self.setWindowTitle('Создание списка')
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setMinimumSize(350, 200)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
                            Qt.WindowStaysOnTopHint)

    def init_widget(self):
        hbox_date = QHBoxLayout()
        hbox_num = QHBoxLayout()
        hbox_type = QHBoxLayout()
        hbox_btn = QHBoxLayout()
        hbox_btn.setContentsMargins(0, 20, 0, 0)
        # ДАТА
        d_label = QLabel('Дата списка: ')
        d_label.setFixedHeight(self.widget_height)
        d_label.setFont(self.font)
        calendar = QCalendarWidget()
        calendar.setFirstDayOfWeek(Qt.Monday)
        calendar.setGridVisible(True)
        calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.date_picker.setFont(self.font)
        self.date_picker.setFixedHeight(self.widget_height)
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setCalendarWidget(calendar)
        hbox_date.addWidget(d_label)
        hbox_date.addWidget(self.date_picker)
        # НОМЕР СПИСКА
        n_label = QLabel('Номер списка: ')
        n_label.setFixedHeight(self.widget_height)
        n_label.setFont(self.font)
        self.number.setFont(self.font)
        self.number.setFixedHeight(self.widget_height)
        self.number.setMaximum(999999)
        self.number.setMinimum(1)
        self.number.setValue(self.get_last_list_num() + 1)
        hbox_num.addWidget(n_label)
        hbox_num.addWidget(self.number)
        # ВИД ОТПРАВЛЕНИЯ
        m_label = QLabel('Вид отправления: ')
        m_label.setFixedHeight(self.widget_height)
        m_label.setFont(self.font)
        self.type_box.setFont(self.font)
        self.type_box.setFixedHeight(self.widget_height)
        self.type_box.addItems(M_TYPE_KEYS)
        self.type_box.setCurrentIndex(M_TYPE_KEYS.index('Письмо'))
        hbox_type.addWidget(m_label)
        hbox_type.addWidget(self.type_box)
        # КНОПКИ
        self.btn_ok.setFont(self.font)
        self.btn_ok.setFixedSize(self.button_width, self.widget_height)
        self.btn_cancel.setFont(self.font)
        self.btn_cancel.setFixedSize(self.button_width, self.widget_height)
        hbox_btn.addWidget(self.btn_ok)
        hbox_btn.addWidget(self.btn_cancel)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_date)
        vbox.addLayout(hbox_num)
        vbox.addLayout(hbox_type)
        vbox.addLayout(hbox_btn)
        self.setLayout(vbox)
        self.btn_ok.setFocus()

    def init_connect(self):
        self.btn_ok.clicked.connect(self.submit_close)
        self.btn_cancel.clicked.connect(self.close)
        self.date_picker.dateChanged.connect(self.value_change)
        self.type_box.currentIndexChanged.connect(self.value_change)

    def value_change(self):
        self.btn_ok.setFocus()

    def get_last_list_num(self, query_date: date=None):
        query_date = query_date or date.today()
        list_rpo = ListRpo.query.filter(ListRpo.date == query_date).order_by(ListRpo.num.desc()).first()
        if list_rpo:
            return list_rpo.num
        return 0

    def submit_close(self):
        self.date = self.date_picker.date().toPyDate()
        self.num = self.number.value()
        self.mail_type = M_TYPE.get(self.type_box.currentText(), 2)
        self.accept()

    def keyPressEvent(self, event):
        # Enter, NumEnter
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.submit_close()


# Даилог редактирования списка РПО
class EditListDialog(QDialog):

    font = AppConfig.FONT

    def __init__(self, rpo_list: ListRpo, auto_complete=True, parent=None):
        super(EditListDialog, self).__init__(parent)
        self.parent = parent
        self._root = os.path.dirname(__file__)
        self.rpo_list = rpo_list
        self.auto_complete = auto_complete
        self.table_head = ['id', '№', 'ШПИ', 'Вес', 'Плата', 'Ошибки', 'Индекс', 'Получатель', 'Адрес']

        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH

        # Быстрое сохранение
        self.fast_save = False
        # Режим редактирования
        self.edit_mode = False
        # Текущая строка в таблице
        self.current_table_row = None

        # Регулярки для валидаторов
        self.int_regexp = QRegExp("[0-9]+")
        self.double_regexp = QRegExp("[0-9.,]+")

        # Таблица с РПО
        self.table = RpoTableWidget(1, len(self.table_head))
        # Быстрое сохранение
        self.fast_save_widget = QCheckBox('Быстрое сохранение отправления')
        # Сообщение об сохранении
        self.message = QLabel('')
        self.timer = QTimer()
        # Автозавершение
        self.completer = QCompleter()
        self.completer_model = QStringListModel()
        # ИНФОРМАЦИЯ О СПИСКЕ
        # List ID
        self.lid_widget = EditWidget('LID:', str(self.rpo_list.id), locked=False)
        # Номер
        self.num_widget = EditWidget('Список:', str(self.rpo_list.num), locked=False)
        # Кол-во РПО
        self.rpo_widget = EditWidget('РПО:', str(self.rpo_list.rpo_count), locked=False)
        # Общий вес
        self.sum_mass_widget = EditWidget('Вес:', str(self.rpo_list.mass), locked=False)
        # Дата списка
        self.date_widget = EditWidget('Дата:', format_date(self.rpo_list.date), locked=False)
        # Вид отправления
        self.type_widget = EditWidget('Вид ПО:', MailTypes_Dict.get(self.rpo_list.mail_type, 'Неизв.'), locked=False)
        # Общая плата
        self.sum_mass_rate_widget = EditWidget('Плата:', '%.2f' % self.rpo_list.mass_rate, locked=False)

        # ИНФОРМАЦИЯ О РПО
        # Rpo ID
        self.rid_widget = EditWidget('RID:', '', locked=False)
        # Регион
        self.region_widget = EditWidget('Регион', 'Нет', locked=False)
        # ШПИ
        self.barcode_widget = EditWidget('ШПИ:', '', locked=False)
        # Индекс
        self.index_widget = EditWidget('Индекс:', '', locked=False)
        # Город
        self.city_widget = EditWidget('Город:', '', locked=False)
        # Кнопка поиска
        self.btn_search = ButtonWidget('Поиск')
        # Адрес
        self.address_widget = EditWidget('Адрес:', '', locked=True)
        # Получатель
        self.reception_widget = EditWidget('Получатель:', '', locked=True)
        # Вес
        self.mass_widget = EditWidget('Вес:', '', locked=True)
        # Плата
        self.pay_widget = EditWidget('Плата:', '', locked=True)
        # Плата с НДС
        self.pay_nds_widget = EditWidget('Плата с НДС:', '', locked=False)
        # Кнопка сохранить
        self.btn_save = ButtonWidget('Сохранить')

        # Тарификатор
        self.tarif = Tarificator(TarificatorConfig)
        # Инициализация
        self.init_ui()
        self.init_widget()
        self.init_connect()
        self.init_table()

    def init_ui(self):
        self.setWindowTitle('Редактирование списка')
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setMinimumSize(640, 480)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
                            Qt.WindowStaysOnTopHint | Qt.WindowMaximizeButtonHint)
        self.setWindowState(Qt.WindowMaximized)

    def init_widget(self):
        grid = QGridLayout()
        vbox = QVBoxLayout()
        text_width = 80
        field_width = 0

        int_validator = QRegExpValidator(self.int_regexp)
        double_validator = QRegExpValidator(self.double_regexp)
        upper_validator = UpperCaseValidator()

        self.colorize = AppConfig.COLORIZE

        # Автозавершение
        self.completer.setModel(self.completer_model)

        # Быстрое сохранение
        self.fast_save_widget.setFont(self.font)
        self.fast_save_widget.setFocusPolicy(Qt.NoFocus)

        # Сообщение
        self.message.setFixedHeight(50)
        self.message.setFont(self.font)
        self.message.setStyleSheet('.QLabel {color: #1d1d1d; border: none;}')

        # Таблица с РПО
        self.table.setFont(self.font)
        self.table.setHorizontalHeaderLabels(self.table_head)
        self.table.setColumnHidden(0, True)
        self.table.setFocusPolicy(Qt.NoFocus)

        # ИНФОРМАЦИЯ О СПИСКЕ
        # List ID
        self.set_style_edit(self.lid_widget, field_width, text_width)

        # Номер
        self.set_style_edit(self.num_widget, field_width, text_width)

        # Кол-во РПО
        self.set_style_edit(self.rpo_widget, field_width, text_width)

        # Общий вес
        self.set_style_edit(self.sum_mass_widget, field_width, text_width)

        # Дата списка
        self.set_style_edit(self.date_widget, field_width, text_width)

        # Вид отправления
        self.set_style_edit(self.type_widget, field_width, text_width)

        # Общая плата
        self.set_style_edit(self.sum_mass_rate_widget, field_width, text_width)

        # ИНФОРМАЦИЯ О РПО
        # Rpo ID
        self.set_style_edit(self.rid_widget, field_width, text_width)

        # Регион
        self.set_style_edit(self.region_widget, 0, text_width)

        # ШПИ
        self.barcode_widget.field.setMaxLength(14)
        self.barcode_widget.field.setValidator(int_validator)
        self.set_style_edit(self.barcode_widget, field_width, 60, enabled=True)

        # Индекс
        self.index_widget.field.setMaxLength(6)
        self.index_widget.field.setValidator(int_validator)
        self.set_style_edit(self.index_widget, field_width, text_width, enabled=True)

        # Город
        self.set_style_edit(self.city_widget, field_width, text_width, enabled=True)
        self.city_widget.field.setValidator(upper_validator)

        # Кнопка поиска
        self.btn_search.button.setFixedWidth(self.button_width)
        self.btn_search.button.setFocusPolicy(Qt.NoFocus)

        # Адрес
        self.set_style_edit(self.address_widget, field_width, text_width, enabled=True)
        self.address_widget.field.setValidator(upper_validator)
        self.address_widget.block_data()

        # Получатель
        self.set_style_edit(self.reception_widget, field_width, 120, enabled=True)
        self.reception_widget.field.setValidator(upper_validator)
        if self.auto_complete:
            self.reception_widget.field.setCompleter(self.completer)

        # Вес
        self.set_style_edit(self.mass_widget, field_width, text_width, enabled=True)
        self.mass_widget.field.setValidator(double_validator)

        # Плата
        self.set_style_edit(self.pay_widget, field_width, text_width, enabled=True)
        self.pay_widget.field.setValidator(double_validator)
        self.pay_widget.block_data()

        # Плата с НДС
        self.set_style_edit(self.pay_nds_widget, field_width, 120, enabled=False)

        # Кнопка сохранить
        self.btn_save.button.setFixedWidth(self.button_width)
        self.btn_save.button.setFocusPolicy(Qt.NoFocus)

        grid.addWidget(self.lid_widget, 0, 0, 1, 2)
        grid.addWidget(self.num_widget, 0, 2, 1, 2)
        grid.addWidget(self.rpo_widget, 0, 4, 1, 2)
        grid.addWidget(self.sum_mass_widget, 0, 6, 1, 1)
        grid.addWidget(self.date_widget, 1, 0, 1, 2)
        grid.addWidget(self.type_widget, 1, 2, 1, 2)
        grid.addWidget(self.message, 1, 4, 1, 2)
        grid.addWidget(self.sum_mass_rate_widget, 1, 6, 1, 1)

        grid.addWidget(HLine(), 2, 0, 1, 7)

        grid.addWidget(self.rid_widget, 3, 0, 1, 2)
        grid.addWidget(self.region_widget, 3, 4, 1, 3)
        grid.addWidget(self.barcode_widget, 4, 0, 1, 2)
        grid.addWidget(self.index_widget, 4, 2, 1, 2)
        grid.addWidget(self.city_widget, 4, 4, 1, 2)
        grid.addWidget(self.btn_search, 4, 6)
        grid.addWidget(self.reception_widget, 5, 0, 1, 4)
        grid.addWidget(self.address_widget, 5, 4, 1, 3)
        grid.addWidget(self.mass_widget, 6, 0, 1, 2)
        grid.addWidget(self.pay_widget, 6, 2, 1, 2)
        grid.addWidget(self.pay_nds_widget, 6, 4, 1, 2)
        grid.addWidget(self.btn_save, 6, 6)

        grid.addWidget(HLine(), 7, 0, 1, 7)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(5, 0, 5, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.fast_save_widget)
        hbox.addStretch(1)
        hbox.addWidget(self.message)

        vbox.addLayout(hbox)
        vbox.addWidget(HLine())
        vbox.addLayout(grid)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

    def init_table(self):
        if not self.rpo_list.id:
            session.add(self.rpo_list)
            session.commit()

        self.lid_widget.field.setText(str(self.rpo_list.id))
        self.num_widget.field.setText(str(self.rpo_list.num))
        self.rpo_widget.field.setText(str(self.rpo_list.rpo_count))
        self.sum_mass_widget.field.setText(str(self.rpo_list.mass))
        self.date_widget.field.setText(format_date(self.rpo_list.date))
        self.type_widget.field.setText(MailTypes_Dict.get(self.rpo_list.mail_type, 'Неизв.'))
        self.sum_mass_rate_widget.field.setText('%.2f' % self.rpo_list.mass_rate)

        rpos = self.rpo_list.all_rpo.order_by(Rpo.num_string.desc()).all()
        self.table.setRowCount(0)

        for num, rpo in enumerate(rpos):
            self.table.add_row(num, rpo, self.colorize)

    def init_connect(self):
        self.table.set_double_click(self.table_double_click)
        self.table.delete_row.connect(self.recount_list)
        self.fast_save_widget.stateChanged.connect(self.change_fast_save_state)
        self.btn_search.button.clicked.connect(self.find_index)
        self.btn_save.button.clicked.connect(self.save_rpo)
        # Поле с индексом
        self.index_widget.field.tab_pressed.connect(self.index_widget_out_focus)
        self.index_widget.field.enter_completed.connect(self.index_widget_complete)
        #
        self.city_widget.field.tab_pressed.connect(self.city_widget_out_focus)
        self.city_widget.field.enter_completed.connect(self.city_widget_complete)
        # Поле с ШПИ
        self.barcode_widget.field.tab_pressed.connect(self.barcode_widget_out_focus)
        self.barcode_widget.field.enter_completed.connect(self.barcode_widget_complete)
        # Поле с адресом
        self.address_widget.field.tab_pressed.connect(self.address_widget_out_focus)
        self.address_widget.field.enter_completed.connect(self.address_widget_complete)
        # Поле с получателем
        self.reception_widget.field.tab_pressed.connect(self.reception_widget_out_focus)
        self.reception_widget.field.enter_completed.connect(self.reception_widget_complete)
        # Поле с весом
        self.mass_widget.field.tab_pressed.connect(self.mass_widget_out_focus)
        self.mass_widget.field.enter_completed.connect(self.mass_widget_complete)
        self.mass_widget.this_blocked.connect(self.refresh_pay)
        # Поле с платой
        self.pay_widget.field.tab_pressed.connect(self.pay_widget_out_focus)
        self.pay_widget.field.enter_completed.connect(self.pay_widget_complete)
        # После с платой + ндс
        self.pay_nds_widget.field.tab_pressed.connect(self.pay_nds_widget_out_focus)
        self.pay_nds_widget.field.enter_completed.connect(self.pay_nds_widget_complete)
        # NUM_PLUS
        self.barcode_widget.field.enter_plus.connect(self.save_rpo)
        self.index_widget.field.enter_plus.connect(self.save_rpo)
        self.city_widget.field.enter_plus.connect(self.save_rpo)
        self.mass_widget.field.enter_plus.connect(self.save_rpo)
        self.pay_widget.field.enter_plus.connect(self.save_rpo)
        self.address_widget.field.enter_plus.connect(self.save_rpo)
        self.reception_widget.field.enter_plus.connect(self.save_rpo)
        # Таймер
        self.timer.timeout.connect(self.clear_message)

    def set_data_completer(self, index):
        completions = Completion.query.filter(Completion.index == index).all()
        if completions:
            complete_list = [com.reception for com in completions]
            self.completer_model.setStringList(complete_list)
        else:
            self.completer_model.setStringList([])

    def save_completion(self, index, reception):
        completion = Completion.query.filter(Completion.index == index).filter(Completion.reception == reception).first()
        if not completion:
            completion = Completion(index, reception)
            session.add(completion)

    def recount_list(self):
        self.rpo_list.recount_rpo()
        session.commit()
        self.rpo_widget.field.setText(str(self.rpo_list.rpo_count))
        self.sum_mass_widget.field.setText(str(self.rpo_list.mass))
        self.sum_mass_rate_widget.field.setText('%.2f' % self.rpo_list.mass_rate)

    def closeEvent(self, event):
        if self.rpo_list.rpo_count == 0:
            session.delete(self.rpo_list)
            session.commit()
        event.accept()

    def add_message(self, msg, color='#1d1d1d'):
        self.timer.start(1000)
        style = '.QLabel {color: %s; border: none;}' % color
        self.message.setStyleSheet(style)
        self.message.setText(msg)

    def add_success_message(self, msg):
        self.add_message(msg, '#008000')

    def add_error_message(self, msg):
        self.add_message(msg, '#FF0000')

    def add_warning_message(self, msg):
        self.add_message(msg, '#D35400')

    def add_info_message(self, msg):
        self.add_message(msg, '#2980B9')

    def clear_message(self):
        self.message.setStyleSheet('.QLabel {color: #1d1d1d; border: none;}')
        self.message.clear()

    def save_rpo(self):
        rid = self.rid_widget.field.text()
        barcode = self.barcode_widget.field.text()
        index = self.index_widget.field.text()
        address = self.address_widget.field.text()
        reception = self.reception_widget.field.text()
        mass = self.mass_widget.field.text()
        mass_rate = self.pay_widget.field.text()

        error_count = 0
        self.clear_error()

        if len(barcode) == 0 or len(barcode) < 14:
            self.barcode_widget.set_error_message('Неверный ШПИ')
            error_count += 1
        else:
            kr = gen_control_rank(barcode)
            if barcode[-1] != kr:
                self.barcode_widget.set_error_message('Неверный КР [{}]'.format(kr))
                error_count += 1

        if len(index) == 0 or len(index) < 6:
            self.index_widget.set_error_message('Неверный индекс')
            error_count += 1

        if len(reception) == 0:
            self.reception_widget.set_error_message('Не может быть пустым')
            error_count += 1

        parse_pass = self.tarif.string_to_num(mass)
        if not parse_pass:
            self.mass_widget.set_error_message('Неверный вес')
            error_count += 1
        else:
            if self.rpo_list.mail_type == 2:
                if parse_pass > TarificatorConfig.END_MAIL_WEIGHT:
                    self.mass_widget.set_error_message('Должен быть не больше: {}'.format(TarificatorConfig.END_MAIL_WEIGHT))
                    error_count += 1
            elif self.rpo_list.mail_type == 3:
                if TarificatorConfig.END_PARCEL_WEIGHT < parse_pass < TarificatorConfig.START_PARCEL_WEIGTH:
                    self.mass_widget.set_error_message('Должен быть от {} до {}'.format(TarificatorConfig.START_PARCEL_WEIGTH,
                                                                                        TarificatorConfig.END_PARCEL_WEIGHT))
                    error_count += 1

        if len(mass_rate) == 0:
            self.pay_widget.set_error_message('Ошибка тарификации')
            error_count += 1

        if rid:
            if error_count == 0:
                rpo = Rpo.query.get(rid)
                if rpo:
                    rpo.barcode = barcode
                    rpo.index = index
                    if not address:
                        rpo.address = ', '.join([index, self.city_widget.field.text()])
                    else:
                        rpo.address = address
                    rpo.reception = reception
                    rpo.mass = parse_pass
                    rpo.mass_rate = self.tarif.get_mass_rate(parse_pass, self.rpo_list.mail_type)
                    rpo.check_error()
                    self.save_completion(index, reception)
                    self.recount_list()
                    if self.current_table_row is not None:
                        self.table.add_row(self.current_table_row, rpo, False)
                    self.clear_fields()
                    self.edit_mode = False
                    self.add_success_message('Сохранено :)')
                    self.barcode_widget.field.setFocus()
                    return True
        else:
            double = Rpo.query.filter(Rpo.barcode == barcode).first()
            if double:
                self.barcode_widget.set_error_message('Такой ШПИ уже существует')
                error_count += 1

            if error_count == 0:
                rpo = Rpo()
                rpo.barcode = barcode
                rpo.index = index
                if not address:
                    rpo.address = ', '.join([index, self.city_widget.field.text()])
                else:
                    rpo.address = address
                rpo.reception = reception
                rpo.mass = parse_pass
                rpo.mass_rate = self.tarif.get_mass_rate(parse_pass, self.rpo_list.mail_type)
                last_rpo = self.rpo_list.all_rpo.order_by(Rpo.id.desc()).first()
                if last_rpo:
                    rpo.num_string = last_rpo.num_string + 1
                else:
                    rpo.num_string = 1
                rpo.check_error()
                self.rpo_list.add_rpo(rpo)
                self.save_completion(index, reception)
                self.recount_list()
                self.table.add_row(0, rpo)
                self.clear_fields()
                self.edit_mode = False
                self.add_success_message('Сохранено :)')
                self.barcode_widget.field.setFocus()
                return True
        self.add_error_message('Ошибка сохранения :(')
        return False

    def clear_fields(self):
        self.rid_widget.field.clear()
        self.barcode_widget.field.clear()
        self.index_widget.field.clear()
        self.region_widget.field.clear()
        self.city_widget.field.clear()
        if self.reception_widget.field.isEnabled(): self.reception_widget.field.clear()
        if self.address_widget.field.isEnabled(): self.address_widget.field.clear()
        if self.mass_widget.field.isEnabled():
            self.mass_widget.field.clear()
            self.pay_widget.field.clear()
            self.pay_nds_widget.field.clear()
        if self.pay_widget.field.isEnabled():
            self.pay_widget.field.clear()
            self.pay_nds_widget.field.clear()

    def clear_error(self):
        self.barcode_widget.clear_message()
        self.index_widget.clear_message()
        self.reception_widget.clear_message()
        self.address_widget.clear_message()
        self.mass_widget.clear_message()
        self.pay_widget.clear_message()
        self.pay_nds_widget.clear_message()

    def find_index(self):
        self.city_widget_complete()

    def refresh_pay(self):
        self.mass_widget_out_focus()

    def split_name(self, name):
        if 'МОСКВА' in name:
            return 'МОСКВА'
        if 'ПОЧТАМТ' in name:
            return name.replace('ПОЧТАМТ', '').strip()
        return name.strip()

    def table_double_click(self, rid):
        self.current_table_row = self.table.currentIndex().row()
        self.load_rpo_by_id(rid)

    def index_widget_out_focus(self):
        index = self.index_widget.field.text()
        self.region_widget.field.clear()
        self.city_widget.field.clear()

        if len(index) < 6:
            self.index_widget.set_error_message('Неверная длина')
            self.focusPreviousChild()
            return False
        db_index = Index.query.filter(Index.index == index).first()
        if not db_index:
            self.index_widget.set_error_message('Индекс не найден в БД')
            self.city_widget.field.setFocus()
            return False
        else:
            self.region_widget.field.setText(db_index.region)
            name = self.split_name(db_index.name)
            self.city_widget.field.setText(name)
            self.index_widget.set_success_message('Все в порядке :)')
            self.set_data_completer(index)
            if self.fast_save:
                if not self.address_widget.field.isEnabled() and not self.reception_widget.field.isEnabled() and not self.mass_widget.field.isEnabled() and not self.pay_widget.field.isEnabled():
                    self.city_widget.field.focusNextChild()
                    self.save_rpo()
                    return True

            self.city_widget.field.focusNextChild()
            return True

    def index_widget_complete(self):
        self.index_widget.field.focusNextChild()
        self.index_widget_out_focus()

    def city_widget_out_focus(self):
        pass

    def city_widget_complete(self):
        city = self.city_widget.field.text()
        if not city:
            return False

        index = self.index_widget.field.text()

        if city.find('%') == -1:
            city = '{}%'.format(city)

        query = Index.query.filter(Index.name.like(city))

        if len(index) == 6:
            try:
                first = index[:3]
                last = index[3:]
                if int(first) < 131:
                    query = query.filter(Index.index.like('%{}'.format(last)))
            except Exception:
                pass

        indexex = query.order_by(Index.index).all()

        if len(indexex) == 0:
            indexex = Index.query.filter(Index.name.like(city)).all()

        d = IndexSelectDialog(indexex, index, parent=self)
        if d.exec_():
            if d.value:
                index = Index.query.filter(Index.index == d.value).first()
                if index:
                    self.index_widget.field.setText(index.index)
                    self.city_widget.field.setText(index.name)
                    self.region_widget.field.setText(index.region)

                    if self.reception_widget.field.isEnabled():
                        self.reception_widget.field.setFocus()
                    elif self.address_widget.field.isEnabled():
                        self.address_widget.field.setFocus()
                    elif self.mass_widget.field.isEnabled():
                        self.mass_widget.field.setFocus()
                    else:
                        self.save_rpo()

    def barcode_widget_out_focus(self):
        barcode = self.barcode_widget.field.text()
        if not barcode:
            self.barcode_widget.set_error_message('Не указан ШПИ')
            self.barcode_widget.field.focusPreviousChild()
            return False
        kr = gen_control_rank(barcode)
        if barcode[-1] != kr:
            self.barcode_widget.set_error_message('Неверный КР [{}]'.format(kr))
            self.barcode_widget.field.focusPreviousChild()
            return False

        rpo = Rpo.query.filter(Rpo.barcode == barcode).first()
        if not self.edit_mode and rpo:
            self.barcode_widget.set_error_message('Такой ШПИ уже есть')
            self.barcode_widget.field.focusPreviousChild()
            return False
        self.barcode_widget.set_success_message('Все в порядке :)')
        return True

    def barcode_widget_complete(self):
        #self.barcode_widget.field.focusNextChild()
        self.index_widget.field.setFocus()
        self.barcode_widget_out_focus()

    def address_widget_out_focus(self):
        pass

    def address_widget_complete(self):
        self.address_widget.field.focusNextChild()
        self.address_widget_out_focus()

    def reception_widget_out_focus(self):
        reception = self.reception_widget.field.text()
        if not reception:
            self.reception_widget.set_error_message('Не может быть пустым')
            self.reception_widget.field.focusPreviousChild()
            return False
        if self.fast_save:
            if not self.mass_widget.field.isEnabled() and not self.pay_widget.field.isEnabled() and not self.address_widget.field.isEnabled():
                self.save_rpo()

    def reception_widget_complete(self):
        self.reception_widget.field.focusNextChild()
        self.reception_widget_out_focus()

    def mass_widget_out_focus(self):
        mass = self.mass_widget.field.text()
        parse_pass = self.tarif.string_to_num(mass)
        if parse_pass:
            self.mass_widget.field.setText(str(parse_pass))

            if self.rpo_list.mail_type == 2 and parse_pass > TarificatorConfig.END_MAIL_WEIGHT:
                self.mass_widget.set_error_message('Максимальный вес: {}'.format(TarificatorConfig.END_MAIL_WEIGHT))
                self.mass_widget.field.setFocus()
                self.mass_widget.field.selectAll()
                return False
            if self.rpo_list.mail_type == 3:
                if parse_pass < TarificatorConfig.START_PARCEL_TARIF:
                    self.mass_widget.set_error_message(
                        'Минимальный вес: {}'.format(TarificatorConfig.START_PARCEL_WEIGTH))
                    self.mass_widget.field.setFocus()
                    self.mass_widget.field.selectAll()
                    return False
                if parse_pass > TarificatorConfig.END_PARCEL_WEIGHT:
                    self.mass_widget.set_error_message(
                        'Максимальный вес: {}'.format(TarificatorConfig.END_PARCEL_WEIGHT))
                    self.mass_widget.field.setFocus()
                    self.mass_widget.field.selectAll()
                    return False
            self.mass_widget.set_success_message('Все в порядке :)')
            self.mass = parse_pass
            mass_rate = self.tarif.get_mass_rate(parse_pass, self.rpo_list.mail_type, False)
            mass_rate_nds = self.tarif.get_mass_rate(parse_pass, self.rpo_list.mail_type, True)
            if mass_rate:
                self.pay_widget.field.setText('%.2f' % mass_rate)
                self.pay = mass_rate
                self.pay_nds = mass_rate_nds
                self.pay_nds_widget.field.setText('%.2f' % mass_rate_nds)
                self.pay_nds_widget.set_success_message('Все в порядке :)')
                self.pay_widget.set_success_message('Все в порядке :)')

                if self.fast_save and not self.pay_widget.field.isEnabled():
                    self.save_rpo()
                    return False
                return True
            else:
                self.pay_nds_widget.set_success_message('Ошибка тарификации')
                self.pay_widget.set_success_message('Ошибка тарификации')
                self.mass_widget.field.setFocus()
                self.mass_widget.field.selectAll()
                return False
        else:
            self.mass_widget.set_error_message('Неверный формат веса')
            return False

    def mass_widget_complete(self):
        self.mass_widget.field.focusNextChild()
        self.mass_widget_out_focus()

    def pay_widget_out_focus(self):
        pay = self.pay_widget.field.text()
        temp = pay.replace(' ', '').replace(',', '.')
        try:
            self.pay = float(temp)
            self.pay_widget.field.setText('%.2f' % self.pay)
            self.pay_nds = round(self.pay * 1.18, 2)
            self.pay_nds_widget.field.setText('%.2f' % self.pay_nds)
        except ValueError:
            self.pay_widget.set_error_message('Неверный формат платы')
            return False

    def pay_widget_complete(self):
        self.pay_widget.field.focusNextChild()
        self.pay_widget_out_focus()

    def pay_nds_widget_out_focus(self):
        pass

    def pay_nds_widget_complete(self):
        self.pay_nds_widget.field.focusNextChild()
        self.pay_nds_widget_out_focus()

    def change_fast_save_state(self, state: int):
        self.fast_save = self.fast_save_widget.isChecked()

    def set_style_edit(self, edit: EditWidget, field_width=100, text_width=50, enabled=False):
        edit.field.setAlignment(Qt.AlignCenter)
        if field_width and field_width > 0:
            edit.field.setFixedWidth(field_width)
        if text_width and text_width > 0:
            edit.text.setFixedWidth(text_width)
        edit.setEnabled(enabled)

    def load_rpo_by_id(self, rid):
        self.edit_mode = True
        rpo = Rpo.query.get(rid)
        if rpo:
            self.rid_widget.field.setText(str(rpo.id))
            self.barcode_widget.field.setText(str(rpo.barcode))
            self.index_widget.field.setText(str(rpo.index))
            index = Index.query.filter(Index.index == rpo.index).first()
            if index:
                self.city_widget.field.setText(index.name)
            else:
                self.city_widget.field.setText('')
            self.reception_widget.field.setText(rpo.reception)
            self.address_widget.field.setText(rpo.address)
            self.mass_widget.field.setText(str(rpo.mass))
            self.pay_widget.field.setText('%.2f' % rpo.mass_rate)
            self.pay_nds_widget.field.setText('%.2f' % round(rpo.mass_rate * 1.18, 2))

    def keyPressEvent(self, event):
        # Ctrl + F
        if (event.modifiers() == Qt.ControlModifier) and event.key() == Qt.Key_F:
            self.city_widget.field.setFocus()
            self.city_widget.field.selectAll()
