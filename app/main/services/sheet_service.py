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
        delivery_items=[]
        for item in delivery_sheet.items:
            delivery_item=DeliveryItem()
            delivery_item.delivery_no=item["delivery_no"]
            delivery_item.delivery_item_no=item["delivery_item_no"]
            delivery_item.product_type=item["product_type"]
            delivery_item.company_id=item["company_id"]
            delivery_item.spec=item["spec"]
            delivery_item.item_id=item["item_id"]
            delivery_item.f_whs=item["f_whs"]
            delivery_item.max_quantity=item["max_quantity"]
            delivery_item.volume=item["volume"]
            delivery_item.f_loc=item["f_loc"]
            delivery_item.material=item["material"]
            delivery_item.weight=item["weight"]
            delivery_item.quantity=item["quantity"]
            delivery_item.free_pcs=item["free_pcs"]
            delivery_item.total_pcs=item["total_pcs"]
            delivery_item.create_time=item["create_time"]
            delivery_item.update_time=item["update_time"]
        delivery_items.append(delivery_item)
        delivery_sheet.items=delivery_items
        sheets_list.append(delivery_sheet)

    return sheets_list
