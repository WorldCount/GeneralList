#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import (QCheckBox, QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QLineEdit, QFrame,
                             QGraphicsDropShadowEffect, QAction)
from PyQt5.QtGui import (QIcon, QFont, QRegExpValidator, QColor, QValidator)
from PyQt5.QtCore import (Qt, pyqtSignal, QRegExp, QEvent)
from config import AppConfig


__author__ = 'WorldCount'


class UpperCaseValidator(QValidator):

    def validate(self, p_str, p_int):
        return QValidator.Acceptable, p_str.upper(), p_int


class HLine(QFrame):

    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class VLine(QFrame):

    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class LineEdit(QLineEdit):

    tab_pressed = pyqtSignal()
    enter_completed = pyqtSignal()
    enter_plus = pyqtSignal()

    def __init__(self, *args):
        super(LineEdit, self).__init__(*args)
        self.textChanged.connect(self.text_complete)
        self.max_length = None

    def event(self, event):
        if event.type() == QEvent.KeyPress:

            if event.key() == Qt.Key_Tab:
                self.tab_pressed.emit()
                self.focusNextChild()
                return True

            if event.key() in (16777221, 16777220):
                self.enter_completed.emit()
                return True

            if event.key() == 43:
                self.enter_plus.emit()
                return True

            if event.key() == 124:
                return True

        return QLineEdit.event(self, event)

    def setMaxLength(self, p_int):
        self.max_length = p_int
        QLineEdit.setMaxLength(self, p_int)

    def text_complete(self, text):
        if self.max_length:
            if len(text) == self.max_length and self.cursorPosition() == self.max_length:
                self.enter_completed.emit()


class ButtonWidget(QWidget):

    font = AppConfig.FONT

    def __init__(self, btn_text=None, msg=None, parent=None):
        super(ButtonWidget, self).__init__(parent)
        self._root = os.path.dirname(__file__)
        # Виджеты
        self.button = QPushButton(btn_text)
        self.message = QLabel(msg)
        # Инициализация
        self.init_ui()
        self.init_widget()

    def init_ui(self):
        pass

    def init_widget(self):
        # Кнопка
        self.button.setFixedHeight(30)
        self.button.setFont(self.font)
        # Текст
        self.message.setStyleSheet('.QLabel {color: #1d1d1d; border: none;}')
        self.message.setFixedHeight(20)
        self.message.setContentsMargins(5, 0, 0, 0)
        font = self.font
        font.setPointSize(11)
        self.message.setFont(font)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self.button)
        vbox.addWidget(self.message)
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def clear_message(self):
        style = '.QLabel {color: {}; border: none;}'.format('#1d1d1d')
        self.message.setStyleSheet(style)
        self.message.clear()

    def set_message(self, msg, msg_color='#1d1d1d'):
        style = '.QLabel {color: %s; border: none;}' % msg_color
        self.message.setStyleSheet(style)
        self.message.setText(msg)

    def set_success_message(self, msg):
        self.set_message(msg, '#00A736')

    def set_error_message(self, msg):
        self.set_message(msg, '#E01515')


class EditWidget(QWidget):

    font = AppConfig.FONT
    this_blocked = pyqtSignal()

    def __init__(self, label_text=None, field_text=None, locked=True, parent=None):
        super(EditWidget, self).__init__(parent)
        self._root = os.path.dirname(__file__)
        # Виджеты
        self.text = QLabel()
        self.field = LineEdit()
        self.message = QLabel()
        #
        self.block = False
        self.effect = None
        self.default = None
        self.block_action = None
        self._system_block = None

        self._locked_ico = QIcon(os.path.join(self._root, 'icon', 'locked.png'))
        self._unlocked_ico = QIcon(os.path.join(self._root, 'icon', 'unlocked.png'))

        if label_text:
            self.text.setText(label_text)
        if field_text:
            self.field.setText(field_text)

        self.init_ui()
        self.init_context(locked)
        self.init_widget()

    def init_ui(self):
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.effect = QGraphicsDropShadowEffect()
        self.effect.setBlurRadius(8)
        self.effect.setOffset(1, 1)
        self.setGraphicsEffect(self.effect)
        self.default = self.graphicsEffect()
        self.default.setColor(QColor('#FFF'))
        self.message.setGraphicsEffect(self.default)
        # Выделение всего поля при клике по нему
        self.field.mousePressEvent = lambda _: self.field.selectAll()

    def init_context(self, locked):
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.block_action = QAction(self._locked_ico, 'Заблокировать', self)
        self.block_action.triggered.connect(self.block_data)

        separator1 = QAction('', self)
        separator1.setSeparator(True)

        if locked:
            self.addAction(self.block_action)
            self.addAction(separator1)

    def init_widget(self):
        self.text.setStyleSheet('.QLabel {border: 1px solid; background-color: #34495E; color: #FFF;'
                                'border-color: #1C2833; border-right: none;}')
        self.text.setFixedHeight(30)
        self.text.setFont(self.font)
        self.field.setStyleSheet('.LineEdit {color: #2C3E50; border: 1px solid; border-color: #1C2833;} '
                                 '.LineEdit:disabled {color: #566573; background-color: #B2BABB; border: 1px solid;'
                                 'border-color: #1C2833;}')
        self.field.setFixedHeight(30)
        self.field.setFont(self.font)
        self.message.setStyleSheet('.QLabel {color: #1d1d1d; border: none;}')
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setFixedHeight(20)
        self.message.setContentsMargins(5, 0, 0, 0)
        font = self.font
        font.setPointSize(11)
        self.message.setFont(font)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addWidget(self.text)
        hbox.addWidget(self.field)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addLayout(hbox)
        vbox.addWidget(self.message)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def setEnabled(self, bool_value):
        self.field.setEnabled(bool_value)
        self._system_block = not bool_value
        self.block_action.setEnabled(bool_value)
        if bool_value:
            self.block_action.setText('Заблокировать')
            self.block_action.setIcon(self._locked_ico)
        else:
            self.block_action.setText('Разблокировать')
            self.block_action.setIcon(self._unlocked_ico)

    def block_data(self):
        self.this_blocked.emit()
        if self.block:
            self.block = False
            self.field.setEnabled(True)
            self.block_action.setText('Заблокировать')
            self.block_action.setIcon(self._locked_ico)
        else:
            self.block = True
            self.field.setEnabled(False)
            self.block_action.setText('Разблокировать')
            self.block_action.setIcon(self._unlocked_ico)

    def clear_message(self):
        style = '.QLabel {color: %s; border: none;}' % '#1d1d1d'
        self.message.setStyleSheet(style)
        self.message.clear()

    def set_message(self, msg, msg_color='#1d1d1d'):
        style = '.QLabel {color: %s; border: none;}' % msg_color
        self.message.setStyleSheet(style)
        self.message.setText(msg)

    def set_success_message(self, msg):
        self.set_message(msg, '#008000')

    def set_error_message(self, msg):
        self.set_message(msg, '#FF0000')

    def set_warning_message(self, msg):
        self.set_message(msg, '#D35400')

    def set_info_message(self, msg):
        self.set_message(msg, '#2980B9')


class CheckWidget(QWidget):

    def __init__(self, parent=None):
        super(CheckWidget, self).__init__(parent)

        self._check_box = QCheckBox()
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self._check_box, alignment=Qt.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def check(self):
        self._check_box.setChecked(True)

    def uncheck(self):
        self._check_box.setChecked(False)

    def set_state(self, state):
        self._check_box.setChecked(state)

    def is_checked(self):
        return self._check_box.isChecked()


class BarcodeEdit(QLineEdit):

    clicked = pyqtSignal()
    enter_completed = pyqtSignal()

    def __init__(self, parent=None):
        super(BarcodeEdit, self).__init__(parent)
        self.regex = QRegExp("[0-9]+")
        self.val = QRegExpValidator(self.regex)
        self.setValidator(self.val)
        self.textChanged.connect(self.text_complete)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()
        QLineEdit.mousePressEvent(self, QMouseEvent)

    def keyPressEvent(self, QKeyEvent):
        QLineEdit.keyPressEvent(self, QKeyEvent)

    def text_complete(self, text):
        if len(text) == 14 and self.cursorPosition() == 14:
            self.enter_completed.emit()
