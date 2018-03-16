#!/usr/bin/env python
# -*- coding: utf-8 -*-


from app.models import (ListRpo, Rpo)
from app import session


__author__ = 'WorldCount'


def load_list_rpo(num, mail_type, list_date):
    query = ListRpo.query.filter(ListRpo.date == list_date)
    if num == 0:
        query = query.filter(ListRpo.error_count > 0)
    elif num == 1:
        query = query.filter(ListRpo.double_count > 0)
    elif num == 2:
        query = query.filter(ListRpo.double_count == 0)

    if mail_type or mail_type == 0:
        query = query.filter(ListRpo.mail_type == mail_type)

    return query.order_by(ListRpo.num).all()


def load_list_by_barcode(barcode):
    return ListRpo.query.join(Rpo).filter(Rpo.barcode == barcode).all()


def load_rpo_by_id(rpo_id: int):
    return Rpo.query.get(rpo_id)


def load_rpo_by_list_id(list_id: int):
    session.query(Rpo).join(ListRpo).filter(ListRpo.id == list_id).order_by(Rpo.num_string).all()
