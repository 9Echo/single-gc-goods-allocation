# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 16:17
# @Author  : Zihao.Liu
from app.main.dao.order_left_item_dao import order_left_item_dao
from app.main.entity.delivery_item import DeliveryItem
from app.main.entity.delivery_sheet import DeliverySheet
from app.main.entity.order import Order
from app.utils.uuid_util import UuidUtil


def generate_delivery_sheet(order):
    ds = DeliverySheet()
    ds.delivery_no = UuidUtil.create_id("delivery")
    ds.free_pcs = 0
    ds.total_quantity = 0
    ds.items = []
    for orderitem in order.order_item:
        di = DeliveryItem()
        di.quantity = orderitem.quantity
        ds.total_quantity += di.quantity
        di.free_pcs = orderitem.free_pcs
        ds.free_pcs += di.free_pcs
        di.product_type = orderitem.product_type
        ds.items.append(di)
    return ds


def compose(order_id):
    """进行订单分货"""
    order = Order()
    order.order_item = order_left_item_dao.get_all()
    # stocks = get_stock()
    return generate_delivery_sheet(order)