# -*- coding: utf-8 -*-
# @Time    : 2020/03/26 16:14
# @Author  : zhouwentao
from threading import Thread

from app.main.dao.order_dao import order_dao
from app.main.entity.delivery_sheet import DeliverySheet
from app.main.entity.delivery_item import DeliveryItem
from app.utils.uuid_util import UUIDUtil
from flask import current_app


def generate_sheets(sheets):
    """根据json数据生成对应的发货通知单"""
    sheets_list=[]
    for sheet in sheets:
        delivery_sheet = DeliverySheet(sheet)

        sheet["items"]=DeliveryItem(sheet["items"])
        sheets_list.append(delivery_sheet)

    return sheets_list
