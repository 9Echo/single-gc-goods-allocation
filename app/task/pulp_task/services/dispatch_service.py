# -*- coding: utf-8 -*-
# @Time    : 2020/02/01
# @Author  : shaoluyu
import copy
from threading import Thread
from flask import g
from app.main.pipe_factory.entity.delivery_item import DeliveryItem
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.main.pipe_factory.model import dispatch_filter
from app.main.pipe_factory.model.weight_filter import weight_filter
from app.main.pipe_factory.rule.lp_problem_solution import create_variable_list, call_pulp_solve
from app.main.pipe_factory.service import redis_service
from app.main.pipe_factory.service.combine_sheet_service import combine_sheets
from app.main.pipe_factory.service.create_delivery_item_service import CreateDeliveryItem
from app.main.pipe_factory.service.replenish_property_service import replenish_property
from app.task.pulp_task.analysis.rules import pulp_solve
from app.util import weight_calculator
from app.util.uuid_util import UUIDUtil
from model_config import ModelConfig


def dispatch(order):
    """根据订单执行分货
    """
    # 1、将订单项转为发货通知单子单的list
    delivery_item_list= CreateDeliveryItem(order)
    # delivery_item_list.is_success=False证明有计算异常,返回一张含有计算出错子项的sheet
    if not delivery_item_list.success:
        return delivery_item_list.failsheet()
    else:
        delivery_item_weight_list,new_max_weight = delivery_item_list.weight()  # 调用weight()，即重量优先来处理
    # 放入重量优先模型
    sheets=weight_filter(delivery_item_weight_list,new_max_weight)

    # 3、补充发货单的属性
    batch_no = UUIDUtil.create_id("ba")
    replenish_property(sheets, order,batch_no)

    # 归类合并
    combine_sheets(sheets,type='weight')
    # 将推荐发货通知单暂存redis
    Thread(target=redis_service.set_delivery_list, args=(sheets,)).start()
    return sheets

