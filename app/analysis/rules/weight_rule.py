# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:15
# @Author  : Zihao.Liu
import copy
import math

from app.utils import weight_calculator
from app.utils.uuid_util import UUIDUtil
from model_config import ModelConfig


def compose(filtered_items: list, left_items: list):
    """重量过滤规则：
    1.总重量不超过35吨
    2.对所有订单项排序，从大到小装到35吨的发货单中，如果总重量超过35吨，则把多出来的货切分为新的子发货单
    filterd_items: 已过滤的子发货单
    left_item: 当前剩余的所有子发货单
    """
    candidate_items = []
    for item in filtered_items:
        # 如果出现重量为0，则该重量为0的单成一单
        if item.weight == 0:
            candidate_items.append(item)
            left_items.remove(item)
            return candidate_items, left_items
    # 依次将子发货单装入发货单中
    total_weight = 0
    new_max_weight = 0
    # 热镀组别和螺旋，MAX_WEIGHT加1000
    if filtered_items and filtered_items[0].product_type in ModelConfig.RD_LX_GROUP:
        new_max_weight = ModelConfig.RD_LX_MAX_WEIGHT
    for item in filtered_items:
        total_weight += item.weight
        if total_weight <= (new_max_weight or ModelConfig.MAX_WEIGHT):
            # 总重量不超过最大重量时，把当前子发货单放入发货单中
            candidate_items.append(item)
            left_items.remove(item)
        else:
            # 当总重量超过发货单最大重量时，对最后一个放入的子发货单进行分单
            item, new_item = split_item(item, total_weight - (new_max_weight or ModelConfig.MAX_WEIGHT))
            if new_item:
                candidate_items.append(item)
                left_items.remove(item)
                left_items.insert(0, new_item)
            break
    return candidate_items, left_items


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


# if __name__ == '__main__':
#     item1 = DeliveryItem()
#     item1.product_type = "热镀"
#     item1.item_id = "02A165*4.25*6000"
#     item1.quantity = 30
#     item1.free_pcs = 5
#     item1.weight = weight_calculator.calculate_weight(item1.product_type, item1.item_id, item1.quantity, item1.free_pcs)
#     item2 = DeliveryItem()
#     item2.product_type = "热度"
#     item2.item_id = "021025*1.9*5950"
#     item2.quantity = 30
#     item2.free_pcs = 6
#     item2.weight = weight_calculator.calculate_weight(item2.product_type, item2.item_id, item2.quantity, item2.free_pcs)
#     print(item1.weight)
#     print(item2.weight)
#     items = [item1, item2]
#     sheets = dispatch_filter.filter(items)
#     for sheet in sheets:
#         sheet.weight = 0
#         for di in sheet.items:
#             sheet.weight += di.weight
#         print(sheet.as_dict())
#         print(sheet.weight)

