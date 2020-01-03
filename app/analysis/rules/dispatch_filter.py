# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 14:03
# @Author  : Zihao.Liu
import copy

from app.analysis.rules import product_type_rule, weight_rule, package_solution
from app.main.entity.delivery_sheet import DeliverySheet
from model_config import ModelConfig


def filter(delivery_items: list):
    """
    根据过滤规则将传入的发货子单划分到合适的发货单中
    """
    # 返回的提货单列表
    sheets = []
    # 提货单明细列表
    item_list = []
    left_items = delivery_items
    new_max_weight = 0
    # 遍历明细列表，如果一个子单的重量不到重量上限，则不参与compose
    for i in copy.copy(delivery_items):
        if i.product_type in ModelConfig.RD_LX_GROUP:
            new_max_weight = ModelConfig.RD_LX_MAX_WEIGHT
        if i.weight < (new_max_weight or ModelConfig.MAX_WEIGHT):
            item_list.append(i)
            left_items.remove(i)
    left_items.sort(key=lambda i: i.weight, reverse=True)
    # 如果有超重的子单，进行compose
    while left_items:
        # filtered_items = product_type_rule.filter(left_items)
        # filtered_items, left_items = weight_rule.compose(filtered_items, left_items)
        # 每次取第一个元素进行compose
        filtered_items, left_items = weight_rule.compose([left_items[0]], left_items)
        # 如果过滤完后没有可用的发货子单则返回
        # if not filtered_items:
        #     return sheets
        if not filtered_items:
           break
        item_list.extend(filtered_items)
        # 根据过滤完后的item生成发货通知单
        # sheet = DeliverySheet()
        # sheet.items = filtered_items
        # sheets.append(sheet)
    # filtered_items = []
    task_id = 0
    while item_list:
        is_full = False
        weight_cost = []
        for item in item_list:
            weight_cost.append((int(item.weight), int(item.weight)))
        # 将所有子单进行背包选举
        final_weight, result_list = package_solution.dynamic_programming(len(item_list),
                                                                         ModelConfig.RD_LX_MAX_WEIGHT, weight_cost)
        print(final_weight)
        print(result_list)
        temp_item_list = copy.copy(item_list)
        # 如果本次选举的组合在合理值范围内，直接赋车次号，不参于后续的操作
        if (ModelConfig.RD_LX_MAX_WEIGHT - 2000) < final_weight < ModelConfig.RD_LX_MAX_WEIGHT:
            task_id += 1
            is_full = True
        for i in range(0, len(result_list)):
            if result_list[i] == 1:
                # filtered_items.append(item_list[i])
                sheet = DeliverySheet()
                sheet.items = [temp_item_list[i]]
                if is_full:
                    sheet.load_task_id = task_id
                sheets.append(sheet)
                item_list.remove(temp_item_list[i])

    return sheets, task_id

