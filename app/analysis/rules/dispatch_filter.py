# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 14:03
# @Author  : Zihao.Liu
import csv

from app.analysis.rules import product_type_rule, weight_rule
from app.main.dao.delivery_sheet_dao import delivery_sheet_dao
from app.main.entity.delivery_item import DeliveryItem
from app.main.entity.delivery_sheet import DeliverySheet
from app.utils.uuid_util import UUIDUtil


def filter(delivery_items):
    """规格过滤器集合"""
    filtered_items = product_type_rule.filter(delivery_items)
    filtered_items = weight_rule.filter(filtered_items)
    if not filtered_items:
        return None, []
    # 根据过滤完后的item生成发货通知单
    sheet = DeliverySheet()
    sheet.items = filtered_items
    sheet.delivery_no = UUIDUtil.create_id("ds")
    sheet.weight = 0
    for item in sheet.items:
        item.delivery_item_no = UUIDUtil.create_id("di")
        item.delivery_no = sheet.delivery_no
        sheet.customer_id = item.customer_id
        sheet.salesman_id = item.salesman_id
        sheet.weight += item.weight
    # 从item列表中移除已生成发货单的item
    for item in filtered_items:
        delivery_items.remove(item)
    return sheet, delivery_items


if __name__ == '__main__':
    file = open('data_final.csv', 'r', encoding='utf-8')
    reader = csv.reader(file)
    total_items = []
    for row in reader:
        item = DeliveryItem()
        item.id = row[2]
        item.spec = row[6]
        item.product_type = row[7]
        item.quantity = row[11]
        if item.quantity == '':
            item.quantity = 0
        item.free_pcs = row[12]
        if item.free_pcs == '':
            item.free_pcs = 0
        item.customer_id = row[5]
        item.salesman_id = row[14]
        total_items.append(item)
    item_dict = {}
    for item in total_items:
        item_dict.setdefault(item.id, []).append(item)
    for items in item_dict.values():
        while items:
            sheet, items = filter(items)
            if sheet:
                delivery_sheet_dao.insert(sheet)