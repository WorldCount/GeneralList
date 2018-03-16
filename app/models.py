#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, date
from sqlalchemy import Column, String, Integer, ForeignKey, Date, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app import Base, session
from config import TarificatorConfig
from app.post_data.tarificator import Tarificator, MailTypes

__author__ = 'WorldCount'


TARIF = Tarificator(TarificatorConfig())


# Класс ошибок в РПО
class Errors:
    UNDEF = 0
    CLEAR_INDEX = 1
    CLEAR_MASS = 2
    CLEAR_MASS_RATE = 3
    WRONG_MASS_RATE = 4


# Словарь определения ошибок в РПО
Errors_Dict = {Errors.UNDEF: 'Неизв.', Errors.CLEAR_INDEX: 'Пустой индекс', Errors.CLEAR_MASS: 'Пустой вес',
               Errors.CLEAR_MASS_RATE: 'Пустая плата', Errors.WRONG_MASS_RATE: 'Неверный тариф'}


class ListRpo(Base):
    __tablename__ = 'list_rpo'

    id = Column(Integer, primary_key=True)
    num = Column(Integer, nullable=True, index=True, default=0)
    mail_type = Column(Integer, nullable=True, default=MailTypes.UNDEF)
    date = Column(Date, nullable=False, index=True, default=date.today())
    mass_rate = Column(Float, nullable=True, default=0)
    mass = Column(Integer, nullable=True, default=0)
    rpo_count = Column(Integer, nullable=True, default=0)
    error_count = Column(Integer, nullable=True, default=0)
    double_count = Column(Integer, nullable=True, default=0)
    author = Column(String, default="Неизв.")
    load_date = Column(DateTime, nullable=False, default=datetime.now())
    change_date = Column(DateTime, nullable=False, default=datetime.now())

    all_rpo = relationship('Rpo', backref='list', lazy='dynamic', cascade="save-update, merge, delete")

    def __repr__(self):
        return '<ListRpo (Id: {}, Num: {})>'.format(self.id, self.num)

    def __init__(self, num=None, list_date=None, mail_type=None, author=None, mass=None, mass_rate=None,
                 error_count=None):

        self.num = 0
        self.mail_type = MailTypes.UNDEF
        self.mass_rate = 0.0
        self.mass = 0
        self.rpo_count = 0
        self.double_count = 0
        self.error_count = 0
        self.author = "Неизв."

        if num: self.num = num
        if list_date: self.date = list_date
        if mail_type: self.mail_type = mail_type
        if author: self.author = author
        if error_count: self.error_count = error_count
        if mass: self.mass = mass
        if mass_rate: self.mass_rate = mass_rate

    def recount_rpo(self):
        self.mass = 0
        self.mass_rate = 0
        self.rpo_count = 0
        self.error_count = 0
        self.double_count = 0

        for num, rpo in enumerate(self.all_rpo.all()):
            rpo.num_string = num + 1
            self.mass += rpo.mass
            self.mass_rate += rpo.mass_rate
            self.rpo_count += 1
            self.error_count += rpo.error_count
            self.double_count += 1 if rpo.double else 0

    def add_rpo(self, rpo):
        if self.exist_rpo(rpo):
            rpo.double = True

        if self.mail_type == 0:
            self.find_mail_type(rpo)

        self.all_rpo.append(rpo)
        self.mass += rpo.mass
        self.mass_rate += rpo.mass_rate
        self.rpo_count += 1
        self.double_count += 1 if rpo.double else 0

    def del_rpo(self, rpo):
        if self.exist_rpo(rpo):
            if rpo.double:
                self.double_count -= 1
            session.delete(rpo)
            self.mass -= rpo.mass
            self.mass_rate -= rpo.mass_rate
            self.rpo_count -= 1

    def exist_rpo(self, rpo):
        return self.all_rpo.filter(Rpo.barcode == rpo.barcode).count() > 0

    def find_mail_type(self, rpo):
            if rpo.mass != 0 and rpo.mass_rate != 0:
                mail_type = TARIF.check_type(rpo.mass, rpo.mass)
                if mail_type != MailTypes.UNDEF:
                    self.mail_type = mail_type

    def get_all_errors(self):
        return Error.query.filter(Error.rpo.has(list_id=self.id)).all()

class Rpo(Base):
    __tablename__ = 'rpo'

    id = Column(Integer, primary_key=True)
    barcode = Column(String(14), nullable=True, index=True)
    index = Column(String(6), nullable=True)
    address = Column(String(140), nullable=True)
    reception = Column(String(140), nullable=True)
    mass = Column(Integer, nullable=True, default=0)
    mass_rate = Column(Float, nullable=True, default=0)
    num_string = Column(Integer)
    error_count = Column(Integer, default=0, index=True)
    double = Column(Boolean, default=False, nullable=False)

    list_id = Column(Integer, ForeignKey('list_rpo.id'))
    all_error = relationship('Error', backref='rpo', lazy='dynamic', cascade="save-update, merge, delete")

    def __repr__(self):
        return '<Rpo: (Id: {}, Barcode: {}, Index: {}, Mass: {}, MassRate: {})>'.format(self.id, self.barcode,
                                                                                        self.index, self.mass,
                                                                                        self.mass_rate)

    def __init__(self, barcode=None, num_string=None, index=None, address=None, reception=None, mass=None,
                 mass_rate=None, rpo_list=None):
        self.error_count = 0
        self.barcode = ""
        self.index = ""
        self.address = ""
        self.reception = ""
        self.mass = 0
        self.mass_rate = 0.0
        self.double = False

        if barcode: self.barcode = barcode
        if index: self.index = index
        if address: self.address = address
        if reception: self.reception = reception
        if mass: self.mass = mass
        if mass_rate: self.mass_rate = mass_rate
        if rpo_list: self.list = rpo_list
        if num_string: self.num_string = num_string

    def add_error(self, error):
        if not self.exist_error(error):
            self.all_error.append(error)
            self.list.error_count += 1
            self.error_count += 1

    def del_error(self, error):
        if self.exist_error(error):
            session.delete(error)
            self.list.error_count -= 1
            self.error_count -= 1

    def exist_error(self, error):
        return self.all_error.filter(Error.type == error.type).count() > 0

    def find_error(self):
        if not self.barcode or self.barcode == " ":
            self.add_error(Error(Errors.CLEAR_INDEX, 'Пустой индекс', 'Индекс не может быть пустым'))
        if not self.mass:
            self.add_error(Error(Errors.CLEAR_MASS, 'Пустой вес', 'Вес не может быть пустым'))
        if not self.mass_rate:
            self.add_error(Error(Errors.CLEAR_MASS_RATE, 'Пустая плата', 'Плата не может быть пустой'))

        if self.mass == 100:
            new_mass_rate = TARIF.get_mass_rate(self.mass)
            if self.mass_rate == new_mass_rate:
                old_mass_rate = new_mass_rate
            else:
                old_mass_rate = TARIF.get_mass_rate(self.mass, MailTypes.PARCEL)
        else:
            old_mass_rate = TARIF.get_mass_rate(self.mass, MailTypes.AUTO)

        if self.mass and self.mass_rate != old_mass_rate:
            self.add_error(Error(Errors.WRONG_MASS_RATE, 'Неверный тариф',
                                 'Тариф должен быть: {}'.format(old_mass_rate)))

    def check_error(self):
        for error in self.all_error.all():
            if error.type == Errors.CLEAR_INDEX and (self.index and (len(self.index) == 6)):
                self.del_error(error)

            if error.type == Errors.CLEAR_MASS and self.mass:
                self.del_error(error)

            if error.type == Errors.CLEAR_MASS_RATE and self.mass_rate:
                self.del_error(error)

            if error.type == Errors.WRONG_MASS_RATE:

                if self.mass == 100:
                    new_mass_rate = TARIF.get_mass_rate(self.mass)
                    if self.mass_rate == new_mass_rate:
                        old_mass_rate = new_mass_rate
                    else:
                        old_mass_rate = TARIF.get_mass_rate(self.mass, MailTypes.PARCEL)
                else:
                    old_mass_rate = TARIF.get_mass_rate(self.mass, MailTypes.AUTO)

                if self.mass and self.mass_rate == old_mass_rate:
                    self.del_error(error)
        self.find_error()

    def is_double(self):
        return Rpo.query.filter(Rpo.barcode == self.barcode).count() > 0


class Error(Base):
    __tablename__ = 'error'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False, default=Errors.UNDEF, index=True)
    msg = Column(String(100))
    comment = Column(String(140), nullable=True)

    rpo_id = Column(Integer, ForeignKey('rpo.id'))

    def __init__(self, error_type=None, msg=None, comment=None, rpo=None):
        self.type = Errors.UNDEF
        self.msg = ""
        self.comment = ""

        if rpo: self.rpo = rpo
        if error_type: self.type = error_type
        if msg: self.msg = msg
        if comment: self.comment = comment

    def __repr__(self):
        return '<Error: (Id: {}, Type: {}, Msg: {})>'.format(self.id, self.type, self.msg)


class Index(Base):
    __tablename__ = 'index'

    index = Column(String(6), nullable=False, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    head = Column(String, nullable=True)
    region = Column(String, nullable=False)

    def __init__(self, index=None, name=None, head=None, region=None):
        if index: self.index = index
        if name: self.name = name
        if head: self.head = head
        if region: self.region = region

    def __repr__(self):
        return '<Index: (Index: {}, Name: {})>'.format(self.index, self.name)


class Completion(Base):
    __tablename__ = 'completion'

    id = Column(Integer, primary_key=True)
    index = Column(String(6), nullable=False, index=True)
    reception = Column(String, nullable=False, index=True)

    def __init__(self, index=None, reception=None):
        if index: self.index = index
        if reception: self.reception = reception

    def __repr__(self):
        return '<Completion: (Index: {}, Reception: {})>'.format(self.index, self.reception)


class Config(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    value = Column(String, nullable=False, index=True)

    def __init__(self, name=None, value=None):
        if name: self.name = name.lower()
        if value: self.value = value

    def __repr__(self):
        return '<Config: (Name: {}, Value: {})>'.format(self.name, self.value)

    @staticmethod
    def get_value(name):
        config = Config.query.filter(Config.name == name.lower()).first()
        if config:
            return config.value
        return False

    @staticmethod
    def set_value(name, value):
        config = Config.query.filter(Config.name == name.lower()).first()
        if config:
            config.value = value
        else:
            config = Config(name, value)
            session.add(config)
        session.commit()
