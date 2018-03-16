#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import operator
from datetime import (date, datetime)
from PyQt5.QtWidgets import (QWidget, QMenu, QTableView, QAbstractItemView, QTableWidget, QHeaderView,
                             QTableWidgetItem, QAction, QMessageBox)
from PyQt5.QtCore import (Qt, QAbstractTableModel, QDate, QDateTime, QVariant, pyqtSignal, QModelIndex)
from PyQt5.QtGui import (QColor, QIcon)
from app.wcutils.date import format_date
from app.models import (ListRpo, Rpo)
from app import session
from app.interface.dialogs import (NumListEditDialog, DateListEditDialog, MailTypeListEditDialog)
from app.interface.widgets import CheckWidget
from app.post_data.tarificator import MailTypes_Dict

__author__ = 'WorldCount'


class TableModel(QAbstractTableModel):

    def __init__(self, header_list, parent=None):
        super(TableModel, self).__init__(parent)
        self.parent = parent
        self.header = header_list
        self.d = []

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.d)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.header)

    def data(self, ind, role=None):
        data_type = type(self.d[ind.row()][ind.column()])

        if role == Qt.DisplayRole and ind.isValid():
            if data_type == QDateTime:
                return self.d[ind.row()][ind.column()].toString('dd.MM.yyyy hh:mm:ss')
            elif data_type == QDate:
                return self.d[ind.row()][ind.column()].toString('dd.MM.yyyy')
            elif data_type in (date, datetime):
                return format_date(self.d[ind.row()][ind.column()])
            else:
                return self.d[ind.row()][ind.column()]

        if role == Qt.EditRole:
            return self.d[ind.row()][ind.column()]

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return None

    def headerData(self, col_num, orient, role=None):
        if orient == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col_num]

        if orient == Qt.Vertical and role == Qt.DisplayRole:
            return col_num + 1

        return QVariant()

    def sort(self, col_num, order=None):
        self.layoutAboutToBeChanged.emit()
        self.d = sorted(self.d, key=operator.itemgetter(col_num))

        if order == Qt.DescendingOrder:
            self.d.reverse()

        self.layoutChanged.emit()

    def set_data(self, data):
        self.beginResetModel()
        self.d = data
        self.endResetModel()


class TableView(QTableView):

    def __init__(self, parent=None):
        super(TableView, self).__init__(parent)
        self.parent = parent
        self._init_ui()

    def _init_ui(self):
        self.setGridStyle(Qt.SolidLine)
        self.setObjectName('TableView')


class TableWidget(QWidget):

    def __init__(self, header, parent=None):
        super(TableWidget, self).__init__(parent)
        self.header = header
        self.table_column = [x for x in range(len(self.header) - 1)]
        self.table = TableView(self)
        self.table_model = TableModel(self.header, self.table)
        self.table.setModel(self.table_model)
        self.data = []

    def init_table(self):
        self.data = self.get_data()
        self.table_model.set_data(self.data)
        self.resize_column(self.table_column)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.set_sort_mode(True)

    def get_data(self):
        return []

    # Метод: Прячет указанные столбцы
    def hide_column(self, list_column):
        for col in list_column:
            if type(col) == int:
                self.table.hideColumn(col)

    # Метод: Показывает указанные столбцы
    def show_column(self, list_column):
        for col in list_column:
            if type(col) == int:
                self.table.showColumn(col)

    # Метод: Отображать или спрятать нумерацию строк
    def set_view_num(self, bool_value):
        if bool_value:
            self.table.verticalHeader().show()
        else:
            self.table.verticalHeader().hide()

    # Метод: Устанавливает режим сортировки таблицы
    def set_sort_mode(self, bool_value: bool) -> None:
        if bool_value:
            self.table.setSortingEnabled(True)
            self.table.sortByColumn(0, Qt.AscendingOrder)
        else:
            self.table.setSortingEnabled(False)

    # Метод: растягивает столбцы по содержимому
    def resize_column(self, list_column):
        for col in list_column:
            self.table.resizeColumnToContents(col)

    # Метод: Обновляет данные таблицы
    def update_data(self):
        self.data = self.get_data()
        self.table_model.set_data(self.data)
        self.resize_column(self.table_column)

    # ОБРАБОТЧИКИ СОБЫТИЙ
    # Событие: вызов контекстного меню у таблицы
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = menu.addAction('Выход')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quit_action:
            pass

    # Событие: изменение размера виджета
    def resizeEvent(self, event):
        width = self.width()
        height = self.height()
        self.table.resize(width, height)


class GenTableWidget(QTableWidget):
    double_click = pyqtSignal(str)

    def __init__(self, *args):
        super(GenTableWidget, self).__init__(*args)
        self._root = os.path.dirname(__file__)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.header = self.horizontalHeader()
        self.header_list = []
        self.configure()
        self.init_action()

    def configure(self):
        self.setRowCount(0)
        self.header.setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSortingEnabled(False)
        self.doubleClicked.connect(self.emit_fid)

    def init_action(self):
        change_num = QAction(QIcon(os.path.join(self._root, 'icon', 'number.png')), 'Изменить номер списка', self)
        change_num.triggered.connect(self.edit_num_list)

        separator1 = QAction('', self)
        separator1.setSeparator(True)
        separator2 = QAction('', self)
        separator2.setSeparator(True)
        separator3 = QAction('', self)
        separator3.setSeparator(True)

        change_date = QAction(QIcon(os.path.join(self._root, 'icon', 'date.png')), 'Изменить дату списка', self)
        change_date.triggered.connect(self.edit_date_list)

        change_type = QAction(QIcon(os.path.join(self._root, 'icon', 'type.png')), 'Изменить вид отправления', self)
        change_type.triggered.connect(self.edit_type_list)

        delete_list = QAction(QIcon(os.path.join(self._root, 'icon', 'delete.png')), 'Удалить спискок', self)
        delete_list.triggered.connect(self.delete_list)

        self.addAction(change_num)
        self.addAction(separator1)
        self.addAction(change_date)
        self.addAction(separator2)
        self.addAction(change_type)
        self.addAction(separator3)
        self.addAction(delete_list)

    def setHorizontalHeaderLabels(self, header_list, p_str=None):
        self.header_list = header_list
        super(GenTableWidget, self).setHorizontalHeaderLabels(header_list)
        self.header_resize()

    def header_resize(self):
        last_col = len(self.header_list) - 1
        for num, col in enumerate(self.header_list):
            if num == last_col:
                self.header.setSectionResizeMode(num, QHeaderView.Stretch)
            else:
                self.header.setSectionResizeMode(num, QHeaderView.ResizeToContents)

    def set_double_click(self, func):
        self.double_click.connect(func)

    def add_row(self, row_num, list_rpo: ListRpo, colorize=False):
        fid = QTableWidgetItem(str(list_rpo.id))
        check = CheckWidget()
        check.check()
        l_date = QTableWidgetItem(self.value_format(format_date(list_rpo.date)))
        num = QTableWidgetItem(self.value_format(str(list_rpo.num)))
        m_type = QTableWidgetItem(self.value_format(MailTypes_Dict.get(list_rpo.mail_type, 'Неизв.')))
        r_count = QTableWidgetItem(self.value_format(str(list_rpo.rpo_count)))
        e_count = QTableWidgetItem(self.value_format(str(list_rpo.error_count)))
        d_count = QTableWidgetItem(self.value_format(str(list_rpo.double_count)))
        c_date = QTableWidgetItem(self.value_format(format_date(list_rpo.load_date)))
        ch_date = QTableWidgetItem(self.value_format(format_date(list_rpo.change_date)))
        author = QTableWidgetItem(self.value_format(str(list_rpo.author)))
        mass_rate = QTableWidgetItem(self.value_format('%.2f' % list_rpo.mass_rate))

        l_date.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        num.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        m_type.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        r_count.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        e_count.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        d_count.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        c_date.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        ch_date.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        mass_rate.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.setItem(row_num, 0, fid)
        self.setCellWidget(row_num, 1, check)
        self.setItem(row_num, 2, l_date)
        self.setItem(row_num, 3, num)
        self.setItem(row_num, 4, m_type)
        self.setItem(row_num, 5, r_count)
        self.setItem(row_num, 6, e_count)
        self.setItem(row_num, 7, d_count)
        self.setItem(row_num, 8, mass_rate)
        self.setItem(row_num, 9, c_date)
        self.setItem(row_num, 10, ch_date)
        self.setItem(row_num, 11, author)

        if colorize:
            color = QColor('#FFF')
            if list_rpo.double_count == 0 and list_rpo.error_count == 0: color = QColor('#D5F5E3')
            if list_rpo.error_count > 0: color = QColor('#FAD7A0')
            if list_rpo.double_count > 0: color = QColor('#FFC0CB')

            for num, text in enumerate(self.header_list):
                self.set_cell_color(row_num, num, color)

    def emit_fid(self, index: QModelIndex):
        fid = self.get_id_by_index(index)
        if fid:
            self.double_click.emit(fid)

    def value_format(self, value):
        return ' {} '.format(value)

    # Метод: возвращает id файла по индексу
    def get_id_by_index(self, index: QModelIndex):
        item = self.item(index.row(), 0)
        if item:
            return item.text()
        return False

    # Метод: закрашивает ячейку таблицы
    def set_cell_color(self, row, col, color):
        item = self.item(row, col)
        if item:
            item.setBackground(color)

    def edit_num_list(self):
        ind = self.currentIndex()
        list_rpo = self.get_list_rpo_by_index(ind)
        ind_row = ind.row()
        if list_rpo:
            dialog = NumListEditDialog(list_rpo.num)
            if dialog.exec_():
                list_rpo.num = dialog.value
                list_rpo.change_date = datetime.now()
                session.commit()
                item = self.item(ind_row, 3)
                if item:
                    item.setText(self.value_format(str(dialog.value)))
                self.set_change_date(ind_row, list_rpo.change_date)

    def edit_date_list(self):
        ind = self.currentIndex()
        ind_row = ind.row()
        list_rpo = self.get_list_rpo_by_index(ind)
        if list_rpo:
            dialog = DateListEditDialog(list_rpo.date)
            if dialog.exec_():
                list_rpo.date = dialog.value.toPyDate()
                list_rpo.change_date = datetime.now()
                session.commit()
                item = self.item(ind_row, 2)
                if item:
                    item.setText(self.value_format(format_date(dialog.value.toPyDate())))
                self.set_change_date(ind_row, list_rpo.change_date)

    def edit_type_list(self):
        ind = self.currentIndex()
        ind_row = ind.row()
        list_rpo = self.get_list_rpo_by_index(ind)
        if list_rpo:
            dialog = MailTypeListEditDialog(list_rpo.mail_type)
            if dialog.exec_():
                list_rpo.mail_type = dialog.value
                list_rpo.change_date = datetime.now()
                session.commit()
                item = self.item(ind_row, 4)
                if item:
                    item.setText(self.value_format(MailTypes_Dict.get(dialog.value, 'Неизв.')))
                self.set_change_date(ind_row, list_rpo.change_date)

    def delete_list(self):
        ind = self.currentIndex()
        ind_row = ind.row()
        list_rpo = self.get_list_rpo_by_index(ind)
        if list_rpo:
            msg = self.create_mgs_box(list_rpo)
            btn_y = msg.button(QMessageBox.Yes)
            msg.exec_()
            if msg.clickedButton() == btn_y:
                session.delete(list_rpo)
                session.commit()
                self.removeRow(ind_row)

    def set_change_date(self, ind_row, change_date):
        item_change = self.item(ind_row, 9)
        if item_change:
            item_change.setText(self.value_format(format_date(change_date)))

    def get_list_rpo_by_index(self, index):
        fid = self.get_id_by_index(index)
        if fid:
            return ListRpo.query.get(fid)
        return None

    def create_mgs_box(self, list_rpo: ListRpo):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle('Удаление файла')
        txt = 'Вы действительно хотите удалить файл:\n№{}, {}, на {} шт?'
        msg.setText(txt.format(list_rpo.num, MailTypes_Dict.get(list_rpo.mail_type, 'Неизв.'), list_rpo.rpo_count))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        btn_y = msg.button(QMessageBox.Yes)
        btn_y.setText('Да')
        btn_n = msg.button(QMessageBox.No)
        btn_n.setText('Нет')
        msg.setDefaultButton(QMessageBox.No)
        return msg
