# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
from app.main.dao.delivery_sheet_dao import delivery_sheet_dao
from app.main.dao.stock_dao import stock_dao
from app.main.entity.delivery_item import DeliveryItem
from app.main.entity.delivery_sheet import DeliverySheet
from app.utils.uuid_util import UUIDUtil


def dispatch(order):
    """根据订单执行分货
    """
    # TODO 获取当前库存
    stocks = stock_dao.get_all()
    # TODO 经过过滤，得到符合条件的库存
    # 创建发货通知单
    delivery = DeliverySheet()
    delivery.delivery_no = UUIDUtil.create_id("ds")
    delivery.batch_no = UUIDUtil.create_id("batch")
    delivery.status = 0
    delivery.data_address = 00
    delivery.total_quantity = 0
    delivery.free_pcs = 0
    delivery.total_pcs = 0
    delivery.weight = 0
    # 执行分货逻辑，将结合订单信息、过滤信息、库存信息得出结果
    for order_item in order.items:
        item = DeliveryItem()
        item.delivery_no = delivery.delivery_no
        item.delivery_item_no = UUIDUtil.create_id("di")
        item.order_no = order.order_no
        item.product_type = order_item.product_type
        item.spec = order_item.spec
        item.quantity = order_item.quantity
        item.free_pcs = order_item.free_pcs
        item.warehouse = find_warehouse(item.spec, stocks)
        item.weight = weight_calc(item.spec, item.quantity)
        delivery.total_quantity += item.quantity
        delivery.free_pcs += item.free_pcs
        delivery.items.append(item)
    # 保存发货通知单
    delivery_sheet_dao.insert(delivery)
    return delivery


def weight_calc(spec, quantity):
    """估算货物重量"""
    import random
    return random.randint(10, 30)


def find_warehouse(spec, stocks):
    """根据规格查询货物所在仓库"""
    for stock in stocks:
        if stock.spec == spec:
            return stock.warehouse
    return ""
