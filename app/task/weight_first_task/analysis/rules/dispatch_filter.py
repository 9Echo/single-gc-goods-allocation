# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 14:03
# @Author  : Zihao.Liu


from app.main.entity.delivery_sheet import DeliverySheet
from app.task.weight_first_task.analysis.rules import product_type_rule, weight_rule


def filter(delivery_items: list):
    """
    根据过滤规则将传入的发货子单划分到合适的发货单中
    """
    sheets = []
    left_items = delivery_items
    left_items.sort(key=lambda i: i.weight, reverse=True)
    while left_items:
        filtered_items = product_type_rule.filter(left_items)
        filtered_items, left_items = weight_rule.compose(filtered_items, left_items)
        # 如果过滤完后没有可用的发货子单则返回
        if not filtered_items:
            return sheets
        # 根据过滤完后的item生成发货通知单
        sheet = DeliverySheet()
        sheet.items = filtered_items
        sheet.volume = sum([i.volume for i in filtered_items])
        sheets.append(sheet)
    return sheets

