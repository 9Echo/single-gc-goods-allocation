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
        delivery_sheet = DeliverySheet()
        delivery_sheet.items=[]
        delivery_sheet.load_task_id=sheet["load_task_id"]
        delivery_sheet.company_id=sheet["company_id"]
        delivery_sheet.batch_no=sheet["batch_no"]
        delivery_sheet.status=sheet["status"]
        delivery_sheet.customer_id=sheet["customer_id"]
        delivery_sheet.salesman_id=sheet["salesman_id"]
        delivery_sheet.total_pcs=sheet["total_pcs"]
        delivery_sheet.weight=sheet["weight"]
        delivery_sheet.volume=sheet["volume"]
        delivery_sheet.create_time=sheet["create_time"]
        delivery_sheet.update_time=sheet["update_time"]
        for item in sheet["items"]:
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
            delivery_sheet.items.append(delivery_item)
        sheets_list.append(delivery_sheet)

    return sheets_list
