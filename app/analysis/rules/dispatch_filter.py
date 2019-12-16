# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 14:03
# @Author  : Zihao.Liu

from app.analysis.rules import product_type_rule, weight_rule
from app.main.entity.delivery_sheet import DeliverySheet


def filter(delivery_items: list):
    """
    根据过滤规则将传入的发货子单划分到合适的发货单中
    """
    sheets = []
    while delivery_items:
        filtered_items = product_type_rule.filter(delivery_items)
        filtered_items = weight_rule.filter(filtered_items)
        # 如果过滤完后没有可用的发货子单则返回
        if not filtered_items:
            return sheets
        # 根据过滤完后的item生成发货通知单
        sheet = DeliverySheet()
        sheet.items = filtered_items
        # 从item列表中移除已生成发货单的item
        for item in filtered_items:
            delivery_items.remove(item)
        # 如果生成的有效的发货单，保存到发货单列表中
        if sheet:
            sheets.append(sheet)
    return sheets

