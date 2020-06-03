# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
import copy
import math
import pandas as pd
from threading import Thread

from app.main.pipe_factory.model.optimize_filter import optimize_filter_max, optimize_filter_min
from app.main.pipe_factory.model.spec_filter import spec_filter
from app.main.pipe_factory.model.weight_filter import weight_filter
from app.main.pipe_factory.service.dispatch_load_task_service import dispatch_load_task_spec, \
    dispatch_load_task_optimize
from app.util.aspect.method_before import get_item_a, set_weight
from app.main.pipe_factory.service import redis_service
from app.main.pipe_factory.service.combine_sheet_service import combine_sheets
from app.main.pipe_factory.service.create_delivery_item_service import CreateDeliveryItem
from app.main.pipe_factory.service.replenish_property_service import replenish_property
from app.util.uuid_util import UUIDUtil
from threading import Thread


@set_weight
@get_item_a
def dispatch_spec(order):
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



def dispatch_weight(order):
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


def dispatch_optimize(order):
    """根据订单执行分货
    """
    sheets = []
    task_id = 0
    batch_no = UUIDUtil.create_id("ba")
    # 1、将订单项转为发货通知单子单的list
    delivery_item_list = CreateDeliveryItem(order)
    # delivery_item_list.is_success=False证明有计算异常,返回一张含有计算出错子项的sheet
    if not delivery_item_list.success:
        return delivery_item_list.failsheet()
    else:
        # 调用optimize()，即将大小管分开
        max_delivery_items, min_delivery_items = delivery_item_list.optimize()

    if max_delivery_items:
        # 2、使用模型过滤器生成发货通知单
        sheets, task_id = optimize_filter_max(max_delivery_items)
        # 3、补充发货单的属性
        batch_no = UUIDUtil.create_id("ba")  # batch_no 在后面的装车需要
        replenish_property(sheets, order, batch_no)

        # 4、为发货单分配车次
        task_id = dispatch_load_task_optimize(sheets, task_id)

    #
    if min_delivery_items:
        # 小管装填大管车次,这个操作没整合到optimize_filter（只处理了大管）,中间还差了一步发配车次，
        optimize_filter_min(sheets, min_delivery_items, task_id, order, batch_no)
    # 车次提货单合并
    combine_sheets(sheets)
    sheets.sort(key=lambda i: i.load_task_id)
    # 6、将推荐发货通知单暂存redis
    Thread(target=redis_service.set_delivery_list, args=(sheets,)).start()
    return sheets
