# -*- coding: utf-8 -*-
# @Time    : 2020/03/26 16:14
# @Author  : zhouwentao
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.main.pipe_factory.entity.delivery_item import DeliveryItem


def generate_sheets(sheets):
    """根据json数据生成对应的发货通知单"""
    sheets_list = []
    for sheet in sheets:
        delivery_sheet = DeliverySheet(sheet)
        for index in range(len(delivery_sheet.items)):
            delivery_sheet.items[index] = DeliveryItem(delivery_sheet.items[index])
        sheets_list.append(delivery_sheet)

    return sheets_list
