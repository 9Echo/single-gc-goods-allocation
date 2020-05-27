# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
import copy
import math
import pandas as pd
from threading import Thread

from app.main.pipe_factory.model.spec_filter import spec_filter
from app.main.pipe_factory.rule import dispatch_filter, weight_rule
from app.main.pipe_factory.entity.delivery_item import DeliveryItem
from app.main.pipe_factory.service.combine_sheet_service import combine_sheets
from app.main.pipe_factory.service.create_delivery_item_service import CreateDeliveryItem
from app.main.pipe_factory.service import redis_service
from app.main.pipe_factory.service.dispatch_load_task_service import dispatch_load_task_spec
from app.main.pipe_factory.service.replenish_property_service import replenish_property
from app.util import weight_calculator
from app.util.aspect.method_before import get_item_a, set_weight
from app.util.uuid_util import UUIDUtil
from model_config import ModelConfig
from flask import g


@set_weight
@get_item_a
def dispatch(order):
    """根据订单执行分货
    """
    # 1、将订单项转为发货通知单子单的list
    delivery_item_list= CreateDeliveryItem(order)
    # delivery_item_list.is_success=False证明有计算异常,返回一张含有计算出错子项的sheet
    if not delivery_item_list.success:
        return delivery_item_list.failsheet()
    else:
        delivery_item_spec_list=delivery_item_list.spec()#调用spec()，即规格优先来处理
    # 2、使用模型过滤器生成发货通知单
    sheets, task_id = spec_filter(delivery_item_spec_list)
    # 3、补充发货单的属性
    batch_no = UUIDUtil.create_id("ba")
    replenish_property(sheets, order, batch_no)
    # 4、为发货单分配车次
    dispatch_load_task_spec(sheets, task_id)
    # 5、车次提货单按类合并
    combine_sheets(sheets)
    # 6、将推荐发货通知单暂存redis
    Thread(target=redis_service.set_delivery_list, args=(sheets,)).start()
    return sheets



