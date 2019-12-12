# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
from app.analysis.rules import dispatch_filter
from app.main.entity.delivery_item import DeliveryItem
from app.utils import weight_calculator
from app.utils.uuid_util import UUIDUtil


def dispatch(order):
    """根据订单执行分货
    """
    # 将订单项转为发货通知单子单
    delivery_items = []
    for item in order.items:
        di = DeliveryItem()
        di.product_type = item.product_type
        di.spec = item.spec
        di.quantity = item.quantity
        di.free_pcs = item.free_pcs
        di.item_id = item.item_id
        di.material = item.material
        di.f_whs = item.f_whs
        di.f_loc = item.f_loc
        delivery_items.append(di)
    # 使用模型过滤器生成发货通知单
    sheets = dispatch_filter.filter(delivery_items)
    # 补充发货单的属性
    for sheet in sheets:
        sheet.delivery_no = sheet.delivery_no = UUIDUtil.create_id("ds")
        sheet.customer_id = order.customer_id
        sheet.salesman_id = order.salesman_id
        sheet.weight = 0
        sheet.total_pcs = 0
        for di in sheet.items:
            di.delivery_item_no = UUIDUtil.create_id("di")
            di.delivery_no = sheet.delivery_no
            di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.spec, di.quantity, di.free_pcs)
            sheet.weight += di.weight
            sheet.total_pcs += di.total_pcs
    return sheets