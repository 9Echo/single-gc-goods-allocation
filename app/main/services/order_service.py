# -*- coding: utf-8 -*-
# @Time    : 2019/11/19 16:14
# @Author  : Zihao.Liu
from app.main.dao.order_dao import order_dao
from app.main.entity.order import Order
from app.main.entity.order_item import OrderItem
from app.utils.uuid_util import UUIDUtil


def generate_order(order_data):
    """根据json数据生成对应的订单"""
    order = Order()
    order.items = []
    order.order_no = UUIDUtil.create_id("order")
    order.company_id = order_data["company_id"]
    order.customer_id = order_data['customer_id']
    order.salesman_id = order_data['salesman_id']
    for item in order_data['items']:
        oi = OrderItem()
        oi.order_no = order.order_no
        oi.product_type = item['product_type']
        oi.spec = item['spec']
        oi.quantity = item['quantity'] or 0
        oi.free_pcs = item['free_pcs'] or 0
        oi.item_id = item['item_id']
        oi.material = item['material']
        oi.f_whs = item['f_whs']
        oi.f_loc = item['f_loc']
        order.items.append(oi)
    # 生成的订单入库
    order_dao.insert(order)
    return order
