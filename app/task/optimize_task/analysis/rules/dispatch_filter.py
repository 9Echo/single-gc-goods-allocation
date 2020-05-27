# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 14:03
# @Author  : Zihao.Liu
import copy
from flask import g
from app.main.pipe_factory.rule import package_solution, weight_rule
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from model_config import ModelConfig


def optimize_filter(delivery_items: list, task_id=0):
    """
    根据过滤规则将传入的发货子单划分到合适的发货单中
    """
    # 返回的提货单列表
    sheets = []
    # 提货单明细列表
    item_list = []
    # 剩余的发货子单
    left_items = delivery_items
    new_max_weight = 0
    # 遍历明细列表，如果一个子单的重量不到重量上限，则不参与compose
    for i in copy.copy(delivery_items):
        if i.product_type in ModelConfig.RD_LX_GROUP:
            new_max_weight = g.RD_LX_MAX_WEIGHT
        if i.weight < (new_max_weight or g.MAX_WEIGHT):
            item_list.append(i)
            left_items.remove(i)
    if left_items:
        left_items.sort(key=lambda i: i.weight, reverse=True)
    # 如果有超重的子单，进行compose
    while left_items:
        # 每次取第一个元素进行compose,  filtered_items是得到的一个饱和(饱和即已达到重量上限)的子单
        filtered_items, left_items = weight_rule.compose_optimize([left_items[0]], left_items)
        # 如果过滤完后没有可用的发货子单则返回
        if not filtered_items:
            break
        item_list.extend(filtered_items)

    while item_list:
        # 是否满载标记
        is_full = False
        weight_cost = []
        for item in item_list:
            weight_cost.append((int(item.weight), float(item.volume), int(item.weight)))
        # 将所有子单进行背包选举
        final_weight, result_list = \
            package_solution.dynamic_programming(len(item_list),
                                                 (new_max_weight or g.PACKAGE_MAX_WEIGHT),
                                                 ModelConfig.MAX_VOLUME, weight_cost)
        if final_weight == 0:
            break
        # temp_item_list = copy.copy(item_list)
        # 如果本次选举的组合重量在合理值范围内，直接赋车次号，不参于后续的操作
        if ((new_max_weight or g.PACKAGE_MAX_WEIGHT) - ModelConfig.PACKAGE_LOWER_WEIGHT) < \
                final_weight < (new_max_weight or g.PACKAGE_MAX_WEIGHT):
            is_full = True
        # 记录体积之和
        # volume = 0
        # 临时明细存放
        temp_item_list = []
        # 临时提货单存放
        temp_sheet_list = []
        for i in range(len(result_list)):
            if result_list[i] == 1:
                sheet = DeliverySheet()
                # 取出明细列表对应下标的明细
                sheet.items = [item_list[i]]
                # 设置提货单总体积占比
                sheet.volume = item_list[i].volume
                sheet.type = 'recommend_first'
                # 累加明细体积占比
                # volume += item_list[i].volume
                # 分别加入临时提货单和明细
                temp_item_list.append(item_list[i])
                temp_sheet_list.append(sheet)
        # 体积占比满足限制赋车次号
        if is_full:
            task_id += 1
            # 批量赋车次号
            for i in temp_sheet_list:
                i.load_task_id = task_id
        sheets.extend(temp_sheet_list)
        # 整体移除被开走的明细
        for i in temp_item_list:
            item_list.remove(i)

    return sheets, task_id
