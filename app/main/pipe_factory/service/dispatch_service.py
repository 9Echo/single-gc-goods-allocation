# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
import copy
import math
import pandas as pd
from threading import Thread
from app.main.pipe_factory.rule import dispatch_filter, weight_rule, product_type_rule
from app.main.pipe_factory.entity.delivery_item import DeliveryItem
from app.main.pipe_factory.service.combine_sheet_service import combine_sheets
from app.main.pipe_factory.service.create_delivery_item_service import CreateDeliveryItem
from app.main.pipe_factory.service import redis_service
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
    sheets, task_id = dispatch_filter.model_filter(delivery_item_spec_list)
    # 3、补充发货单的属性
    batch_no = UUIDUtil.create_id("ba")
    replenish_property(sheets, order, batch_no)
    # 4、为发货单分配车次
    dispatch_load_task(sheets, task_id)
    # 5、车次提货单按类合并
    combine_sheets(sheets)
    # 6、将推荐发货通知单暂存redis
    Thread(target=redis_service.set_delivery_list, args=(sheets,)).start()
    return sheets


def dispatch_load_task(sheets: list, task_id):
    """
    将发货单根据重量组合到对应的车次上
    :param sheets:
    :param task_id:
    :return:
    """

    doc_type = '提货单'
    left_sheets = []
    for sheet in sheets:
        # 如果已经生成车次的sheet，则跳过不处理
        if sheet.load_task_id:
            continue
        else:
            left_sheets.append(sheet)
    # 记录是否有未分车的单子
    while left_sheets:
        total_weight = 0
        total_volume = 0
        task_id += 1
        no = 0
        # 下差组别的总重量
        rd_lx_total_weight = 0
        for sheet in copy.copy(left_sheets):
            total_weight += sheet.weight
            total_volume += sheet.volume
            # 初始重量
            new_max_weight = g.MAX_WEIGHT
            # 如果是下差过大的品种，重量累加
            if sheet.items and sheet.items[0].product_type in ModelConfig.RD_LX_GROUP:
                rd_lx_total_weight += sheet.weight
            # 如果该车次有下差过大的品种，动态计算重量上限
            if rd_lx_total_weight:
                # 新最大载重上调 下差组别总重量/热镀螺旋最大载重 * 1000
                new_max_weight = round(
                    g.MAX_WEIGHT + (rd_lx_total_weight / g.RD_LX_MAX_WEIGHT) * g.RD_LX_UP_WEIGHT)
                new_max_weight = min(g.RD_LX_MAX_WEIGHT, new_max_weight)
            # 如果当前车次总体积占比超出，计算剩余体积比例进行重量切单
            if total_volume > ModelConfig.MAX_VOLUME:
                # 按照体积比例计算，在最新的最大重量限制下还可以放多少重量
                limit_volume_weight = (ModelConfig.MAX_VOLUME - total_volume + sheet.volume) / sheet.volume * sheet.weight
                # 在最新的最大重量限制下还可以放多少重量
                limit_weight_weight = new_max_weight - (total_weight - sheet.weight)
                # 取较小的
                limit_weight = min(limit_weight_weight, limit_volume_weight)
                sheet, new_sheet = split_sheet(sheet, limit_weight)
                if new_sheet:
                    # 分单成功时旧单放入当前车上，新单放入等待列表
                    sheet.load_task_id = task_id
                    # 给旧单赋单号
                    no += 1
                    sheet.delivery_no = doc_type + str(task_id) + '-' + str(no)
                    # 给明细赋单号
                    for item in sheet.items:
                        item.delivery_no = sheet.delivery_no
                    # 删除原单子
                    left_sheets.remove(sheet)
                    # 加入切分后剩余的新单子
                    left_sheets.insert(0, new_sheet)
                    # 原始单子列表加入新拆分出来的单子
                    sheets.append(new_sheet)
                break
            # 体积不超，处理重量
            else:
                # 如果总重量小于最大载重
                if total_weight <= new_max_weight:
                    # 不超重时将当前发货单装到车上
                    sheet.load_task_id = task_id
                    # 给当前提货单赋单号
                    no += 1
                    sheet.delivery_no = doc_type + str(task_id) + '-' + str(no)
                    # 给明细赋单号
                    for item in sheet.items:
                        item.delivery_no = sheet.delivery_no
                    # 将拼车成功的单子移除
                    left_sheets.remove(sheet)
                    if new_max_weight - total_weight < ModelConfig.TRUCK_SPLIT_RANGE:
                        # 接近每车临界值时停止本次装车
                        break
                # 如果超重
                else:
                    # 超重时对发货单进行分单
                    if sheet.weight < ModelConfig.TRUCK_SPLIT_RANGE:
                        # 重量不超过1吨（可配置）的发货单不分单
                        break
                    # 如果大于1吨
                    else:
                        # 对满足条件的发货单进行分单
                        limit_weight = new_max_weight - (total_weight - sheet.weight)
                        sheet, new_sheet = split_sheet(sheet, limit_weight)
                        if new_sheet:
                            # 分单成功时旧单放入当前车上，新单放入等待列表
                            sheet.load_task_id = task_id
                            # 给旧单赋单号
                            no += 1
                            sheet.delivery_no = doc_type + str(task_id) + '-' + str(no)
                            # 给明细赋单号
                            for item in sheet.items:
                                item.delivery_no = sheet.delivery_no
                            # 删除原单子
                            left_sheets.remove(sheet)
                            # 加入切分后剩余的新单子
                            left_sheets.insert(0, new_sheet)
                            # 原始单子列表加入新拆分出来的单子
                            sheets.append(new_sheet)
                        break
    return task_id


def split_sheet(sheet, limit_weight):
    """
    对超重的发货单进行分单
    limit_weight：当前车次重量剩余载重
    total_volume：当前车次目前体积占比
    """
    total_weight = 0
    # 切分出的新单子
    new_sheet = copy.copy(sheet)
    # 原单子最终的明细
    sheet_items = []
    # 新单子的明细
    new_sheet_items = copy.copy(sheet.items)
    for item in sheet.items:
        # 计算发货单中的哪一子项超重
        total_weight += item.weight
        if total_weight <= limit_weight:
            # 原单子追加明细
            sheet_items.append(item)
            # 新单子减少明细
            new_sheet_items.remove(item)
        #  如果当前车次超重
        else:
            item, new_item = weight_rule.split_item(item, total_weight - limit_weight)
            if new_item:
                # 原单子追加明细
                sheet_items.append(item)
                # 新单子减少明细
                new_sheet_items.remove(item)
                # 新单子加入新切分出来的明细
                new_sheet_items.insert(0, new_item)
            break
    if sheet_items:
        # 原单子明细重新赋值
        sheet.items = sheet_items
        sheet.weight = sum([i.weight for i in sheet.items])
        sheet.total_pcs = sum([i.total_pcs for i in sheet.items])
        sheet.volume = sum([i.volume for i in sheet.items])
        # 新单子明细赋值
        new_sheet.items = new_sheet_items
        new_sheet.weight = sum([i.weight for i in new_sheet.items])
        new_sheet.total_pcs = sum([i.total_pcs for i in new_sheet.items])
        new_sheet.volume = sum([i.volume for i in new_sheet.items])
        return sheet, new_sheet
    else:
        return sheet, None


def sort_by_weight(sheets):
    """
    车次按重量排序
    :param sheets:
    :return:
    """
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

