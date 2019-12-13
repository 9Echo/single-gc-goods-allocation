# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
from app.analysis.rules import dispatch_filter, package_solution
from app.main.entity.delivery_item import DeliveryItem
from app.main.services import redis_service
from app.utils import weight_calculator
from app.utils.uuid_util import UUIDUtil
from config import Config


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
        di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)
        di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)
        delivery_items.append(di)
    # 使用模型过滤器生成发货通知单
    sheets = dispatch_filter.filter(delivery_items)
    # 补充发货单的属性
    batch_no = UUIDUtil.create_id("ba")
    for sheet in sheets:
        sheet.delivery_no = sheet.delivery_no = UUIDUtil.create_id("ds")
        sheet.batch_no = batch_no
        sheet.customer_id = order.customer_id
        sheet.salesman_id = order.salesman_id
        sheet.weight = 0
        sheet.total_pcs = 0
        for di in sheet.items:
            di.delivery_item_no = UUIDUtil.create_id("di")
            di.delivery_no = sheet.delivery_no
            sheet.weight += di.weight
            sheet.total_pcs += di.total_pcs
    # 为发货单分配车次
    dispatch_load_task(sheets)
    # 将推荐发货通知单暂存redis
    redis_service.set_delivery_list(sheets)
    return sheets


def dispatch_load_task(sheets: list):
    """将发货单根据重量组合到对应的车次上"""
    # 先为重量为空的单子生成单独车次
    left_sheets = []
    for sheet in sheets:
        if sheet.weight == 0:
            sheet.load_task_id = UUIDUtil.create_id("lt")
        else:
            left_sheets.append(sheet)
    # 记录是否有未分车的单子
    while left_sheets:
        weight_cost = []
        for sheet in left_sheets:
            weight_cost.append((sheet.weight, sheet.weight))
        final_weight, result_list = package_solution.dynamic_programming(len(left_sheets), Config.MAX_WEIGHT, weight_cost)
        load_task_id = UUIDUtil.create_id("lt")
        # 记录未命中的单子
        missed_sheets = []
        for i in range(0, len(result_list)):
            if result_list[i] == 1:
                left_sheets[i].load_task_id = load_task_id
            else:
                missed_sheets.append(left_sheets[i])
        left_sheets = missed_sheets

