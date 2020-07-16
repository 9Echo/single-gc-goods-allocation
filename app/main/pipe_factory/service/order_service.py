# -*- coding: utf-8 -*-
# @Time    : 2019/11/19 16:14
# @Author  : Zihao.Liu
from threading import Thread
from app.main.pipe_factory.dao.order_dao import order_dao
from app.main.pipe_factory.entity.order import Order
from app.main.pipe_factory.entity.order_item import OrderItem
from app.util.uuid_util import UUIDUtil
from flask import current_app


def generate_order(order_data):
    """根据json数据生成对应的订单"""
    # ModelConfig.INCOMING_WEIGHT = order_data["incoming_weight"]
    order = Order()
    order.items = []
    order.order_no = UUIDUtil.create_id("order")
    order.company_id = order_data["company_id"]
    order.customer_id = order_data['customer_id']
    order.salesman_id = order_data['salesman_id']
    # 车辆载重转换成整形
    order.truck_weight = int(order_data.get('truck_weight'))
    current_app.logger.info('truck_weight = {} '.format(order.truck_weight))
    for item in order_data['items']:
        oi = OrderItem()
        oi.order_no = order.order_no
        oi.product_type = item['product_type']
        oi.spec = item['spec']
        oi.quantity = int(item['quantity'] or 0)
        oi.free_pcs = int(item['free_pcs'] or 0)
        oi.item_id = item['item_id']
        oi.material = item['material']
        oi.f_whs = item['f_whs']
        oi.f_loc = item['f_loc']
        order.items.append(oi)
    # 生成的订单入库
    Thread(target=order_dao.insert, args=(order,))
    return order
