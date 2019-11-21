# -*- coding: utf-8 -*-
# @Time    : 2019/11/19 16:14
# @Author  : Zihao.Liu
from app.main.dao.order_dao import order_dao
from app.main.entity.order import Order
from app.main.entity.order_item import OrderItem
from app.utils.uuid_util import UUIDUtil


def generate_order(order_data):
    """根据json数据生成对应的订单"""
    print(order_data)
    order = Order()
    order.items = []
    order.order_no = UUIDUtil.create_id("order")
    order.customer_id = order_data['customer_id']
    order.salesman_id = order_data['salesman_id']
    for item in order_data['items']:
        order_item = OrderItem()
        order_item.order_no = order.order_no
        order_item.product_type = item['product_type']
        order_item.spec = item['spec']
        order_item.quantity = item['quantity']
        order_item.free_pcs = item['free_pcs']
        order.items.append(order_item)
    # 生成的订单入库
    order_dao.insert(order)
    return order
