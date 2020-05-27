# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
import copy
import math
from threading import Thread
from app.main.pipe_factory.entity.delivery_item import DeliveryItem
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.main.pipe_factory.rule import weight_rule
from app.main.pipe_factory.service import redis_service
from app.main.pipe_factory.service.combine_sheet_service import combine_sheets
from app.main.pipe_factory.service.create_delivery_item_service import CreateDeliveryItem
from app.main.pipe_factory.service.dispatch_load_task_service import dispatch_load_task_optimize
from app.main.pipe_factory.service.replenish_property_service import replenish_property
from app.task.optimize_task.analysis.rules import dispatch_filter, product_type_rule
from app.util import weight_calculator
from app.util.uuid_util import UUIDUtil
from model_config import ModelConfig
import pandas as pd
from flask import g


def dispatch(order):
    """根据订单执行分货
    """
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
        sheets, task_id = dispatch_filter.filter(max_delivery_items)
        # 3、补充发货单的属性
        batch_no = UUIDUtil.create_id("ba") #batch_no 在后面的装车需要
        replenish_property(sheets, order, batch_no)

        # 4、为发货单分配车次
        task_id = dispatch_load_task_optimize(sheets, task_id)
    if min_delivery_items:
        # 小管装填大管车次
        load_task_fill(sheets, min_delivery_items, task_id, order, batch_no)
    # 车次提货单合并
    combine_sheets(sheets)
    sheets.sort(key=lambda i: i.load_task_id)
    # 6、将推荐发货通知单暂存redis
    Thread(target=redis_service.set_delivery_list, args=(sheets,)).start()
    return sheets



def sort_by_weight(sheets):
    sheets_dict = [sheet.as_dict() for sheet in sheets]
    new_sheets = []
    if sheets_dict:
        df = pd.DataFrame(sheets_dict)
        series = df.groupby(by=['load_task_id'])['weight'].sum().sort_values(ascending=False)
        task_id = 0
        for k, v in series.items():
            task_id += 1
            doc_type = '提货单'
            no = 0
            current_sheets = list(filter(lambda i: i.load_task_id == k, sheets))
            for sheet in current_sheets:
                no += 1
                sheet.load_task_id = task_id
                sheet.delivery_no = doc_type + str(task_id) + '-' + str(no)
                for item in sheet.items: item.delivery_no = sheet.delivery_no
                new_sheets.append(sheet)
                sheets.remove(sheet)
    return new_sheets


def load_task_fill(sheets, min_delivery_item, task_id, order, batch_no):
    """
    小管装填大管车次，将小管按照件数从小到大排序
    若小管不够，分完结束
    若小管装填完所有车次后有剩余，进行背包和遍历
    :param batch_no: 分货批次号
    :param order: 订单
    :param sheets:大管的提货单列表
    :param min_delivery_item:小管的子项列表
    :param task_id:当前分配车次号
    :return: None
    """
    if not sheets:
        # 2、使用模型过滤器生成发货通知单
        min_sheets, task_id = dispatch_filter.filter(min_delivery_item)
        # 3、补充发货单的属性
        replenish_property(sheets, order, batch_no)
        # 为发货单分配车次
        dispatch_load_task_optimize(min_sheets, task_id)
        sheets.extend(min_sheets)
    else:
        min_delivery_item.sort(key=lambda i: i.quantity)
        sheets_dict = [sheet.as_dict() for sheet in sheets]
        df = pd.DataFrame(sheets_dict)
        series = df.groupby(by=['load_task_id'])['weight'].sum().sort_values(ascending=False)
        for k, v in series.items():
            max_weight = 0
            current_weight = v
            # 判断该车次是否下差过大
            current_sheets = list(filter(lambda i: i.load_task_id == k, sheets))
            if current_sheets and current_sheets[0].items:
                if current_sheets[0].items[0].product_type in ModelConfig.RD_LX_GROUP:
                    max_weight = g.RD_LX_MAX_WEIGHT
            if v >= (max_weight or g.MAX_WEIGHT):
                continue
            for i in copy.copy(min_delivery_item):
                # 如果该子项可完整放入
                if i.weight <= (max_weight or g.MAX_WEIGHT) - current_weight:
                    # 当前重量累加
                    current_weight += i.weight
                    # 生成新提货单，归到该车次下
                    new_sheet = DeliverySheet()
                    new_sheet.load_task_id = k
                    new_sheet.volume = i.volume
                    new_sheet.batch_no = batch_no
                    new_sheet.customer_id = order.customer_id
                    new_sheet.salesman_id = order.salesman_id
                    new_sheet.weight = i.weight
                    new_sheet.total_pcs = i.total_pcs
                    new_sheet.type = 'recommend_first'
                    new_sheet.items.append(i)
                    sheets.append(new_sheet)
                    # 移除掉被分配的子项
                    min_delivery_item.remove(i)
                else:
                    i, new_item = \
                        weight_rule.split_item_optimize(i, i.weight - ((max_weight or g.MAX_WEIGHT) - current_weight))
                    if new_item:
                        # 生成新提货单，归到该车次下
                        new_sheet = DeliverySheet()
                        new_sheet.load_task_id = k
                        new_sheet.volume = i.volume
                        new_sheet.batch_no = batch_no
                        new_sheet.customer_id = order.customer_id
                        new_sheet.salesman_id = order.salesman_id
                        new_sheet.weight = i.weight
                        new_sheet.type = 'recommend_first'
                        new_sheet.total_pcs = i.total_pcs
                        new_sheet.items.append(i)
                        # 移除掉被分配的子项
                        min_delivery_item.remove(i)
                        # 将剩余的子项放入子项列表
                        min_delivery_item.insert(0, new_item)
                        sheets.append(new_sheet)
                    break
        # 装填完如果小管还有剩余，进行单独分货
        if min_delivery_item:
            # 2、使用模型过滤器生成发货通知单
            min_sheets, task_id = dispatch_filter.filter(min_delivery_item, task_id)
            # 3、补充发货单的属性
            for sheet in min_sheets:
                sheet.batch_no = batch_no
                sheet.customer_id = order.customer_id
                sheet.salesman_id = order.salesman_id
                sheet.weight = 0
                sheet.total_pcs = 0
                for di in sheet.items:
                    di.delivery_item_no = UUIDUtil.create_id("di")
                    sheet.weight += di.weight
                    sheet.total_pcs += di.total_pcs
            # 为发货单分配车次
            dispatch_load_task_optimize(min_sheets, task_id)
            sheets.extend(min_sheets)
