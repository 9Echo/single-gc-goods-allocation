# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:15
# @Author  : Zihao.Liu
import copy
import math

from app.analysis.rules import dispatch_filter
from app.main.entity.delivery_item import DeliveryItem
from app.utils import weight_calculator
from config import Config


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
    # 给candidates从大到小排序
    filtered_items.sort(key=lambda i: i.weight, reverse=True)
    # 依次将子发货单装入发货单中
    total_weight = 0
    for item in filtered_items:
        total_weight += item.weight
        if total_weight <= Config.MAX_WEIGHT:
            # 总重量不超过最大重量时，把当前子发货单放入发货单中
            candidate_items.append(item)
            left_items.remove(item)
        else:
            # 当总重量超过发货单最大重量时，对最后一个放入的子发货单进行分单
            item, new_item = split_item(item, total_weight - Config.MAX_WEIGHT)
            if new_item:
                candidate_items.append(item)
                left_items.remove(item)
                left_items.append(new_item)
            break
    return candidate_items, left_items


def split_item(item, delta_weight):
    """拆分超重的订单"""
    quantity = item.quantity + 1 if item.free_pcs else item.quantity
    over_quantity = math.ceil(quantity * (delta_weight / item.weight))
    if over_quantity < quantity:
        # 超重的数量小于子发货单的数量时对子单进行拆分
        new_item = copy.deepcopy(item)
        new_item.quantity = over_quantity - 1 if item.free_pcs else over_quantity
        new_item.weight = weight_calculator.calculate_weight(new_item.product_type, new_item.item_id, new_item.quantity,
                                                             new_item.free_pcs)
        new_item.total_pcs = weight_calculator.calculate_pcs(new_item.product_type, new_item.item_id, new_item.quantity,
                                                             new_item.free_pcs)
        item.quantity = quantity - over_quantity
        item.free_pcs = 0
        item.weight -= new_item.weight
        item.total_pcs -= new_item.total_pcs
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

