#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import (date, datetime)
from PyQt5.QtWidgets import (QMainWindow, QDesktopWidget, QLabel, QAction, QWidget, QSizePolicy, QCalendarWidget,
                             QDateEdit, QComboBox, QMessageBox, QToolBar, QLCDNumber, QFrame)
from PyQt5.QtCore import (Qt, QSettings, QSize)
from PyQt5.QtGui import QIcon
from config import AppConfig
from app.models import (ListRpo, Config)
from app.interface.dialogs import (DateListEditDialog, MailTypeListEditDialog, EditListDialog, CreateListDialog,
                                   LoadFilesDialog, SaveFilesDialog, DeleteFilesDialog)
from app.interface.widgets import BarcodeEdit
from app.interface.tables import GenTableWidget
from app.wcutils.date import format_date
from app import database
from app import session
from app.post_data.tarificator import MailTypes_Dict

__author__ = 'WorldCount'


LIST_STATUS = {'ВСЕ': None, 'С ошибками': 0, 'С дублями': 1, 'Без дублей': 2}
LIST_STATUS_KEY = sorted(LIST_STATUS.keys())

LIST_TYPE = {'ВСЕ': None, 'Неизв.': 0, 'Письмо': 2, 'Бандероль': 3}
LIST_TYPE_KEY = sorted(LIST_TYPE.keys())


class Window(QMainWindow):

    def __init__(self, parent=None, config_name=None, config_dir=None):
        super(Window, self).__init__(parent)

        self._parent = parent
        self._root = os.path.dirname(__file__)
        self._name = self.__class__.__name__
        self._config_name = config_name
        self._config_dir = config_dir
        # Устанавливаем минимальные размеры окна
        self.setMinimumSize(400, 200)

        if not self._config_name:
            self._config_name = '{}.ini'.format(self._name.lower())

        if not self._config_dir:
            self._config_dir = self._root

        self._config_path = os.path.join(self._config_dir, self._config_name)

        self.settings = QSettings(self._config_path, QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)

        # Инициализация
        self.init_ui()

    # Инициализация: Интерфейс
    def init_ui(self):
        self.setWindowTitle(self._name)
        self.setWindowIcon(QIcon(os.path.join(self._root, 'icon', 'g.png')))

        if os.path.exists(self._config_path):
            pos = self.load_pos()

            if pos:
                screen = QDesktopWidget().screenGeometry()

                if pos.width() == screen.width():
                    self.setWindowState(Qt.WindowMaximized)
                else:
                    self.setGeometry(pos)

    # Инициализация: Виджеты
    def init_widgets(self):
        pass

    # Метод: Сохраняет позицию окна
    def save_pos(self):
        self.settings.setValue('pos/geometry', self.geometry())

    # Метод: Загружает позицию окна
    def load_pos(self):
        return self.settings.value('pos/geometry')

    # Обработчик: Закрытие окна
    def closeEvent(self, close_event):
        self.hide()
        self.save_pos()
        close_event.accept()


class AppWindow(Window):

    app_name = ''
    font = AppConfig.FONT

    def __init__(self, config_name=None, parent=None):
        super(AppWindow, self).__init__(parent, config_name, config_dir=AppConfig.TEMP_DIR)

        # Заголовки таблицы
        self.table_head = ['id', 'Отм', 'Дата', 'Номер', 'Вид', 'РПО', 'Ошибок', 'Дублей', 'Плата', 'Загружен',
                           'Изменен', 'Автор']

        self.use_auto_completion = False

        # Ширина всех виджетов
        self.widget_height = AppConfig.WIDGET_HEIGHT
        self.button_width = AppConfig.BUTTON_WIDTH
        self.colorize = AppConfig.COLORIZE

        # Виджеты
        self.status = self.statusBar()
        self.menu = self.menuBar()
        self.filter_date = QDateEdit(date.today())
        self.status_combo = QComboBox()
        self.type_combo = QComboBox()
        self.table = GenTableWidget(1, len(self.table_head))
        self.barcode = BarcodeEdit()
        self.display_files = QLCDNumber()
        self.display_rpo = QLCDNumber()
        self.display_error = QLCDNumber()
        self.display_double = QLCDNumber()
        # Кнопки
        self.btn_exit = QAction(QIcon(os.path.join(self._root, 'icon', 'exit.png')), 'Выход', self)
        self.btn_load = QAction(QIcon(os.path.join(self._root, 'icon', 'load.png')), 'Загрузить файлы', self)
        self.btn_save = QAction(QIcon(os.path.join(self._root, 'icon', 'save.png')), 'Сохранить списки', self)
        self.btn_find = QAction(QIcon(os.path.join(self._root, 'icon', 'find.png')), 'Загрузить данные', self)
        self.btn_refresh = QAction(QIcon(os.path.join(self._root, 'icon', 'refresh.png')), 'Сбросить фильтры', self)
        self.btn_check = QAction(QIcon(os.path.join(self._root, 'icon', 'check.png')), 'Отметить все', self)
        self.btn_uncheck = QAction(QIcon(os.path.join(self._root, 'icon', 'uncheck.png')), 'Снять отметку', self)
        self.btn_del = QAction(QIcon(os.path.join(self._root, 'icon', 'delete.png')), 'Удалить отмеченные списки', self)
        self.btn_date = QAction(QIcon(os.path.join(self._root, 'icon', 'date.png')), 'Изменить дату списков', self)
        self.btn_new = QAction(QIcon(os.path.join(self._root, 'icon', 'new.png')), 'Создать список', self)
        self.btn_type = QAction(QIcon(os.path.join(self._root, 'icon', 'type.png')), 'Изменить вид отправления', self)
        self.check_complete = QAction('Автодополнение получателя', self)
        self.btn_search = QAction(QIcon(os.path.join(self._root, 'icon', 'find.png')), 'Искать', self)
        # Тулбары
        self.toolbar = QToolBar('Общий')
        self.toolbar_search = QToolBar('Поиск', self)
        self.toolbar_filter = QToolBar('Фильтры', self)
        self.toolbar_status = QToolBar('Статистика', self)
        # Стили
        self.style = 'font-family: Consolas; color: #1d1d1d; font-weight: bold; font-size: 12px'
        # Инициализация: Виджеты
        self.init_widgets()

    # Инициализация: Интерфейс
    def init_ui(self):
        super(AppWindow, self).init_ui()
        self.setMinimumSize(600, 400)
        self.app_name = '{} v{}'.format(AppConfig.APP_NAME, AppConfig.APP_VERSION)
        self.setWindowTitle(self.app_name)
        # Шрифт
        self.setFont(self.font)
        self.setContextMenuPolicy(Qt.NoContextMenu)

    # Инициализация: Виджеты
    def init_widgets(self):
        super(AppWindow, self).init_widgets()
        # Статусбар
        self.status.setStyleSheet(self.style)
        # Авторство :)
        author = QLabel('WorldCount, 2018 ©  ')
        author.setStyleSheet('font-family: Consolas; color: gray; font-weight: normal; font-size: 14px;')
        author.setToolTip('<img src="{}">'.format(os.path.join(self._root, 'icon', 'wc_easter_eggs.png')))
        self.status.addPermanentWidget(author)
        # Меню
        self.menu.setFont(self.font)
        # Инициализация: Кнопки
        self.init_buttons()
        # Инициализация: Слушатели
        self.init_connects()
        # Инициализация: Меню
        self.init_menu()
        # Инициализация: Таблица
        self.init_table()
        # Инициализация: Тулбары
        self.init_toolbars()

    # Инициализация: Кнопки
    def init_buttons(self):
        self.btn_exit.setShortcut('Ctrl+Shift+Q')
        self.btn_exit.setStatusTip('Выход из программы')

        self.btn_load.setShortcut('Ctrl+Shift+L')
        self.btn_load.setStatusTip('Загрузка и парсинг файлов')

        self.btn_save.setShortcut('Ctrl+Shift+S')
        self.btn_save.setStatusTip('Сохранение выделенных списков')

        self.btn_find.setShortcut('Ctrl+Shift+D')
        self.btn_find.setStatusTip('Загрузка данных из базы по фильтрам')

        self.btn_search.setStatusTip('Поиск списков по ШПИ')

        self.btn_refresh.setShortcut('Ctrl+Shift+C')
        self.btn_refresh.setStatusTip('Сброс фильтров по умолчанию')

        #self.btn_check.setShortcut('Ctrl+Shift+C')
        self.btn_check.setStatusTip('Поставить отметку на все списики')

        #self.btn_uncheck.setShortcut('Ctrl+Shift+C')
        self.btn_uncheck.setStatusTip('Снять отметку со всех списков')

        #self.btn_del.setShortcut('Ctrl+Shift+C')
        self.btn_del.setStatusTip('Удаление отмеченных списков')

        self.btn_new.setShortcut('Ctrl+Shift+N')
        self.btn_new.setStatusTip('Создать новый список')

        self.btn_date.setStatusTip('Изменение даты у отмеченных списков')

        self.btn_type.setStatusTip('Изменение вида отправления у отмеченных списков')

        self.check_complete.setStatusTip('Автодополнение получателя при создании списка')
        self.check_complete.setCheckable(True)
        check = Config.get_value('auto_complete_reception')
        if check and check == '1':
            self.check_complete.setChecked(True)
            self.use_auto_completion = True
        else:
            self.check_complete.setChecked(False)
            self.use_auto_completion = False
        self.check_complete.changed.connect(self.change_complete)

    # Инициализация: Меню
    def init_menu(self):
        m_file = self.menu.addMenu('Файл')
        m_file.addAction(self.btn_exit)
        m_list = self.menu.addMenu('Списки')
        m_list.addAction(self.btn_new)
        m_list.addSeparator()
        m_list.addAction(self.btn_load)
        m_list.addAction(self.btn_save)
        m_list.addSeparator()
        m_list.addAction(self.check_complete)
        m_list.addSeparator()

    # Инициализация: Слушатели
    def init_connects(self):
        self.btn_exit.triggered.connect(self.close)
        self.btn_refresh.triggered.connect(self.clear_filter)
        self.btn_find.triggered.connect(self.load_data)
        self.btn_load.triggered.connect(self.load_files)
        self.btn_save.triggered.connect(self.save_files)
        self.btn_check.triggered.connect(self.check_all)
        self.btn_uncheck.triggered.connect(self.uncheck_all)
        self.btn_del.triggered.connect(self.delete_list)
        self.btn_date.triggered.connect(self.change_date)
        self.btn_type.triggered.connect(self.change_type)
        self.btn_search.triggered.connect(self.find_list)
        self.btn_new.triggered.connect(self.create_list)

    # Инициализация: главный тулбар
    def init_general_toolbar(self):
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setMovable(False)
        self.toolbar.setFont(self.font)

        # ПУСТОЙ РАСТЯГИВАЮЩИЙСЯ ВИДЖЕТ
        empty_left = QWidget()
        empty_left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        empty_left.setFixedWidth(50)

        empty_center = QWidget()
        empty_center.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        empty_center.setFixedWidth(50)

        empty_right = QWidget()
        empty_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        empty_right.setFixedWidth(50)

        empty_side = QWidget()
        empty_side.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Добавляем виджеты на тулбар
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btn_load)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btn_save)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btn_new)
        self.toolbar.addSeparator()

        self.toolbar.addWidget(empty_left)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btn_del)
        self.toolbar.addSeparator()

        self.toolbar.addWidget(empty_center)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btn_date)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btn_type)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(empty_right)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btn_check)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btn_uncheck)
        self.toolbar.addWidget(empty_side)

    # Инициализация: тулбар с поиском по РПО
    def init_search_toolbar(self):
        self.toolbar_search.setMovable(False)
        self.toolbar_search.setFont(self.font)

        # ПУСТОЙ РАСТЯГИВАЮЩИЙСЯ ВИДЖЕТ
        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        s_label = QLabel(' Поиск по ШПИ: ')
        s_label.setFixedHeight(self.widget_height)
        s_label.setFont(self.font)

        self.barcode.setMaxLength(14)
        self.barcode.setFont(self.font)
        self.barcode.setFixedSize(160, self.widget_height)
        self.barcode.enter_completed.connect(self.find_list)

        self.toolbar_search.addSeparator()
        self.toolbar_search.addWidget(s_label)
        self.toolbar_search.addWidget(self.barcode)
        self.toolbar_search.addSeparator()
        self.toolbar_search.addAction(self.btn_search)
        self.toolbar_search.addSeparator()
        self.toolbar_search.addWidget(empty)

    # Инициализация: тулбар с фильтрами по данным
    def init_filter_toolbar(self):
        # ТУЛБАР С ПОИСКОМ ПО РПО
        self.toolbar_filter.setMovable(False)

        # ПУСТОЙ РАСТЯГИВАЮЩИЙСЯ ВИДЖЕТ
        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # СТАТУСЫ СПИСКОВ
        c_label = QLabel(' Статус: ')
        c_label.setFont(self.font)
        c_label.setFixedHeight(self.widget_height)
        self.status_combo.setFont(self.font)
        self.status_combo.setFixedSize(140, self.widget_height)
        self.status_combo.addItems(LIST_STATUS_KEY)
        self.status_combo.setCurrentIndex(LIST_STATUS_KEY.index('ВСЕ'))
        # ВИД ОТПРАВЛЕНИЯ
        t_label = QLabel(' Вид ПО: ')
        t_label.setFont(self.font)
        t_label.setFixedHeight(self.widget_height)
        self.type_combo.setFont(self.font)
        self.type_combo.setFixedSize(140, self.widget_height)
        self.type_combo.addItems(LIST_TYPE_KEY)
        self.type_combo.setCurrentIndex(LIST_TYPE_KEY.index('ВСЕ'))
        # ДАТА
        d_label = QLabel(' Дата: ')
        d_label.setFont(self.font)
        d_label.setFixedHeight(self.widget_height)
        date_cal = QCalendarWidget()
        date_cal.setFirstDayOfWeek(Qt.Monday)
        date_cal.setGridVisible(True)
        date_cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.filter_date.setFont(self.font)
        self.filter_date.setFixedSize(130, self.widget_height)
        self.filter_date.setCalendarPopup(True)
        self.filter_date.setCalendarWidget(date_cal)

        self.toolbar_filter.addSeparator()
        self.toolbar_filter.addWidget(t_label)
        self.toolbar_filter.addWidget(self.type_combo)
        self.toolbar_filter.addSeparator()
        self.toolbar_filter.addWidget(c_label)
        self.toolbar_filter.addWidget(self.status_combo)
        self.toolbar_filter.addSeparator()
        self.toolbar_filter.addWidget(d_label)
        self.toolbar_filter.addWidget(self.filter_date)
        self.toolbar_filter.addSeparator()
        self.toolbar_filter.addAction(self.btn_find)
        self.toolbar_filter.addSeparator()
        self.toolbar_filter.addAction(self.btn_refresh)
        self.toolbar_filter.addSeparator()
        self.toolbar_filter.addWidget(empty)

    # Инициализация: тулбар со статистикой
    def init_status_toolbar(self):
        self.toolbar_status.setMovable(False)

        timer_style = 'color: %s; font-weight: bold; background: %s; border: 2px solid %s;'
        # ПУСТОЙ РАСТЯГИВАЮЩИЙСЯ ВИДЖЕТ
        empty_left = QWidget()
        empty_left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        c_label = QLabel(' Всего файлов: ')
        c_label.setFixedHeight(self.widget_height)
        self.display_files.setDigitCount(7)
        self.display_files.setFrameStyle(QFrame.NoFrame)
        self.display_files.setSegmentStyle(QLCDNumber.Flat)
        self.display_files.setStyleSheet(timer_style % ('#44aee3', '#1d1f21', '#555753'))

        r_label = QLabel(' Всего РПО: ')
        r_label.setFixedHeight(self.widget_height)
        self.display_rpo.setDigitCount(7)
        self.display_rpo.setFrameStyle(QFrame.NoFrame)
        self.display_rpo.setSegmentStyle(QLCDNumber.Flat)
        self.display_rpo.setStyleSheet(timer_style % ('#4cb24a', '#1d1f21', '#555753'))

        e_label = QLabel(' Ошибок: ')
        e_label.setFixedHeight(self.widget_height)
        self.display_error.setDigitCount(7)
        self.display_error.setFrameStyle(QFrame.NoFrame)
        self.display_error.setSegmentStyle(QLCDNumber.Flat)
        self.display_error.setStyleSheet(timer_style % ('#ed9d20', '#1d1f21', '#555753'))

        d_label = QLabel(' Повторов: ')
        d_label.setFixedHeight(self.widget_height)
        self.display_double.setDigitCount(7)
        self.display_double.setFrameStyle(QFrame.NoFrame)
        self.display_double.setSegmentStyle(QLCDNumber.Flat)
        self.display_double.setStyleSheet(timer_style % ('#c15c5a', '#1d1f21', '#555753'))

        self.toolbar_status.addSeparator()
        self.toolbar_status.addWidget(c_label)
        self.toolbar_status.addWidget(self.display_files)
        self.toolbar_status.addSeparator()
        self.toolbar_status.addWidget(r_label)
        self.toolbar_status.addWidget(self.display_rpo)
        self.toolbar_status.addSeparator()
        self.toolbar_status.addWidget(e_label)
        self.toolbar_status.addWidget(self.display_error)
        self.toolbar_status.addSeparator()
        self.toolbar_status.addWidget(d_label)
        self.toolbar_status.addWidget(self.display_double)
        self.toolbar_status.addSeparator()
        self.toolbar_status.addWidget(empty_left)
        self.toolbar_status.addSeparator()

    # Инициализация: Все тулбары
    def init_toolbars(self):
        self.init_general_toolbar()
        self.init_search_toolbar()
        self.init_status_toolbar()
        self.init_filter_toolbar()

        self.addToolBar(self.toolbar)
        self.addToolBarBreak()
        self.addToolBar(self.toolbar_search)
        self.addToolBarBreak()
        self.addToolBar(self.toolbar_filter)

        self.addToolBar(Qt.BottomToolBarArea, self.toolbar_status)

    # Инициализация: Таблица
    def init_table(self):
        self.table.setFont(self.font)
        self.table.setHorizontalHeaderLabels(self.table_head)
        self.table.setColumnHidden(0, True)
        self.table.set_double_click(self.table_double_click)
        self.setCentralWidget(self.table)

    # Обработчик: очищает фильтры
    def clear_filter(self):
        self.status_combo.setCurrentIndex(LIST_STATUS_KEY.index('ВСЕ'))
        self.type_combo.setCurrentIndex(LIST_TYPE_KEY.index('ВСЕ'))
        self.filter_date.setDate(date.today())
        self.barcode.clear()

    # Обработчик: использовать автозавершение для получателя
    def change_complete(self):
        self.use_auto_completion = self.check_complete.isChecked()
        config = Config.query.filter(Config.name == 'auto_complete_reception').first()
        if config:
            config.value = self.use_auto_completion
        else:
            config = Config('auto_complete_reception', self.use_auto_completion)
        session.add(config)
        session.commit()

    # Обработчик: загружает файлы из базы
    def load_data(self):
        value_status = self.status_combo.currentText()
        value_type = self.type_combo.currentText()
        num = LIST_STATUS.get(value_status, None)
        mail_type = LIST_TYPE.get(value_type, None)
        list_date = self.filter_date.date().toPyDate()

        self.table.setRowCount(0)
        # Статистика
        count_files = 0
        count_rpo = 0
        count_error = 0
        count_double = 0

        data = database.load_list_rpo(num, mail_type, list_date)
        num_rows = len(data)
        self.table.setRowCount(num_rows)

        for row, rpo_list in enumerate(data):
            # Статистика
            count_files += 1
            count_rpo += rpo_list.rpo_count
            count_error += rpo_list.error_count
            count_double += rpo_list.double_count
            # Добавляем данные
            self.table.add_row(row, rpo_list, self.colorize)
        # Выводим статистику
        self.display_files.display(count_files)
        self.display_rpo.display(count_rpo)
        self.display_error.display(count_error)
        self.display_double.display(count_double)

    # Обработчик: удаляет отмеченные файлы
    def find_list(self):
        barcode = self.barcode.text()

        self.table.setRowCount(0)
        # Статистика
        count_files = 0
        count_rpo = 0
        count_error = 0
        count_double = 0

        data = database.load_list_by_barcode(barcode)
        num_rows = len(data)
        self.table.setRowCount(num_rows)

        for row, rpo_list in enumerate(data):
            # Статистика
            count_files += 1
            count_rpo += rpo_list.rpo_count
            count_error += rpo_list.error_count
            count_double += rpo_list.double_count
            # Добавляем данные
            self.table.add_row(row, rpo_list, self.colorize)
        # Выводим статистику
        self.display_files.display(count_files)
        self.display_rpo.display(count_rpo)
        self.display_error.display(count_error)
        self.display_double.display(count_double)
        self.barcode.selectAll()

    # Обработчик: загружает и обрабатывает файлы
    def load_files(self):
        load_path = Config.get_value('load_dir')
        if not load_path:
            Config.set_value('load_dir', AppConfig.IN_FILE_DIR)
            load_path = AppConfig.IN_FILE_DIR
        dialog = LoadFilesDialog(load_path, self)
        dialog.exec_()

    # Обработчик: сохраняет отмеченные списки
    def save_files(self):
        save_path = Config.get_value('save_dir')
        if not save_path:
            Config.set_value('save_dir', AppConfig.OUT_FILE_DIR)
            save_path = AppConfig.OUT_FILE_DIR
        ids = self.get_check_ids()
        dialog = SaveFilesDialog(ids, save_path, self)
        dialog.exec_()

    # Обработчик: ставит отметки на все списки
    def check_all(self):
        for row_num in range(self.table.rowCount()):
            widget = self.table.cellWidget(row_num, 1)
            if widget:
                widget.check()

    # Обработчик: снимает отметки со всех списков
    def uncheck_all(self):
        for row_num in range(self.table.rowCount()):
            widget = self.table.cellWidget(row_num, 1)
            if widget:
                widget.uncheck()

    # Обработчик: удаляет отмеченные списки
    def delete_list(self):
        row_count = self.get_checked_count()
        if row_count > 0:
            msg = self.create_msg_box(row_count)
            btn_y = msg.button(QMessageBox.Yes)
            msg.exec_()

            if msg.clickedButton() == btn_y:
                self.delete_checked_files()

    # Обработчик: двойной клик на строке таблицы
    def table_double_click(self, fid):
        rpo_list = ListRpo.query.get(fid)
        edit_dialog = EditListDialog(rpo_list, auto_complete=self.use_auto_completion, parent=self)
        edit_dialog.exec_()
        self.load_data()

    # Обработчик: создание нового списка
    def create_list(self):
        info_dialog = CreateListDialog(self)
        if info_dialog.exec_():
            rpo_list = ListRpo(info_dialog.num, info_dialog.date, info_dialog.mail_type, author='Программа')
            edit_dialog = EditListDialog(rpo_list, auto_complete=self.use_auto_completion, parent=self)
            edit_dialog.exec_()
            self.load_data()

    # Обработчик: изменение даты у списков
    def change_date(self):
        if self.table.rowCount() < 1:
            return None

        dialog = DateListEditDialog()
        if dialog.exec_():
            ids = self.get_check_ids()
            rpo_lists = ListRpo.query.filter(ListRpo.id.in_(ids)).all()
            current_date = datetime.now()
            for rpo_list in rpo_lists:
                rpo_list.date = dialog.value.toPyDate()
                rpo_list.change_date = current_date
            session.commit()
            value = format_date(dialog.value.toPyDate())
            self.set_check_value(value, 2, format_date(current_date))

    # Обработчик: изменение вида отправления у списков
    def change_type(self):
        if self.table.rowCount() < 1:
            return None

        dialog = MailTypeListEditDialog()
        if dialog.exec_():
            ids = self.get_check_ids()
            rpo_lists = ListRpo.query.filter(ListRpo.id.in_(ids)).all()
            current_date = datetime.now()
            for rpo_list in rpo_lists:
                rpo_list.mail_type = dialog.value
                rpo_list.change_date = current_date
            session.commit()
            self.set_check_value(MailTypes_Dict.get(dialog.value, 'Неизв.'), 4, format_date(current_date))

    # Обработчик: нажатие клавиш в окне
    def keyPressEvent(self, event):
        # Ctrl + F
        if (event.modifiers() == Qt.ControlModifier) and event.key() == Qt.Key_F:
            self.barcode.setFocus()
            self.barcode.selectAll()

    # Метод: создает MessageBox
    def create_msg_box(self, row_count):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle('Удаление файлов')
        msg.setText('Вы действительно хотите удалить файлы: {} шт?'.format(row_count))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        btn_y = msg.button(QMessageBox.Yes)
        btn_y.setText('Да')
        btn_n = msg.button(QMessageBox.No)
        btn_n.setText('Нет')
        msg.setDefaultButton(QMessageBox.No)
        return msg

    # Метод: возвращает количество отмеченных строк
    def get_checked_count(self):
        count = 0
        for row_num in range(self.table.rowCount()):
            widget = self.table.cellWidget(row_num, 1)
            if widget:
                if widget.is_checked():
                    count += 1
        return count

    # Метод: удаляет отмеченные списки
    def delete_checked_files(self):
        ids = self.get_check_ids()
        dialog = DeleteFilesDialog(ids, self)
        dialog.exec_()
        self.load_data()

    # Метод: возвращает список ID всех отмеченных списков
    def get_check_ids(self):
        ids = []
        for row_num in range(self.table.rowCount()):
            widget = self.table.cellWidget(row_num, 1)
            if widget:
                if widget.is_checked():
                    item = self.table.item(row_num, 0)
                    if item:
                        ids.append(item.text())
        return ids

    # Метод: устанавливает значение у отмеченных списков
    def set_check_value(self, value, column, change_date):
        for row_num in range(self.table.rowCount()):
            widget = self.table.cellWidget(row_num, 1)
            if widget:
                if widget.is_checked():
                    item = self.table.item(row_num, column)
                    if item:
                        item.setText(self.table.value_format(value))
                    item_change = self.table.item(row_num, 9)
                    if item_change:
                        item_change.setText(self.table.value_format(change_date))
