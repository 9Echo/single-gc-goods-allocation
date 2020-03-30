# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:15
# @Author  : Zihao.Liu
import copy
import math
from flask import g
from app.utils import weight_calculator
from app.utils.uuid_util import UUIDUtil
from model_config import ModelConfig


def compose(filtered_item, left_items: list):
    """
    子单拆分重组
    :param filtered_item:待拆分子单
    :param left_items:超重子单列表
    :return:
    """
    new_max_weight = g.RD_LX_MAX_WEIGHT if filtered_item and filtered_item.product_type in ModelConfig.RD_LX_GROUP \
        else g.MAX_WEIGHT
    if filtered_item.weight <= new_max_weight:
        left_items.remove(filtered_item)
        return filtered_item, left_items
    # 依次将子发货单装入发货单中
    else:
        item, new_item = split_item(filtered_item, filtered_item.weight - new_max_weight)
        if new_item:
            left_items.remove(item)
            left_items.insert(0, new_item)
    return item, left_items


def split_item(item, delta_weight):
    """拆分超重的订单，将子项全部转为散根计算"""
    left_pcs = item.total_pcs - math.ceil(item.total_pcs * (delta_weight / item.weight))
    if left_pcs > 0:
        # 根据转化倍数将散根转为整根
        times = weight_calculator.get_quantity_pcs(item.product_type, item.item_id)
        # 计算分单后的子单数量
        quantity = int(left_pcs / times)
        free_pcs = left_pcs % times
        if free_pcs > item.free_pcs:
            free_pcs = item.free_pcs
        left_pcs = quantity * times + free_pcs
        weight = weight_calculator.calculate_weight(item.product_type, item.item_id, quantity, free_pcs)
        # 超重的部分生成新的子单
        new_item = copy.deepcopy(item)
        new_item.total_pcs = item.total_pcs - left_pcs
        new_item.delivery_item_no = UUIDUtil.create_id("di")
        new_item.weight = item.weight - weight
        new_item.quantity = item.quantity - quantity
        new_item.free_pcs = item.free_pcs - free_pcs
        new_item.volume = new_item.quantity / new_item.max_quantity if new_item.max_quantity else 0
        # 更新原子单的数量
        item.quantity = quantity
        item.free_pcs = free_pcs
        item.total_pcs = left_pcs
        item.weight = weight
        item.volume = item.quantity / item.max_quantity if item.max_quantity else 0
        return item, new_item
    else:
        # 超重的数量等于子发货单数量时忽略该子发货单
        return item, None
