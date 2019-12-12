# -*- coding: utf-8 -*-
# Description: 确认发货通知单
# Created: shaoluyu 2019/12/12
from app.analysis.rules import compose_filter
from app.main.dao.compose_dao import compose_dao
from app.main.entity.delivery_item import DeliveryItem
from app.main.entity.delivery_sheet import DeliverySheet


def generate_delivery(delivery_list_data):
    """
    根据json数据生成对应的发货通知单
    """
    delivery_model_list = []
    for delivery in delivery_list_data:
        delivery_model = DeliverySheet(delivery)
        delivery_model.items = []

        for item in delivery['items']:
            delivery_item_model = DeliveryItem(item)
            delivery_model.items.append(delivery_item_model)
        delivery_model_list.append(delivery_model)

    return delivery_model_list

def compose(delivery_list):
    """
    拼单推荐逻辑
    :param delivery_list:
    :return:
    """

    # 客户列表
    customer_id_list = []
    # 品种列表
    product_type_list = []
    # 现有重量
    weight = 0
    # 特殊分组
    group1 = ['热镀', '热度', '热镀1', 'QF热镀管']
    group2 = ['焊管', '焊管1']
    for i in delivery_list:
        customer_id_list.append(i.customer_id)
        weight += i.weight
        for j in i.items:
            if group1.__contains__(j.product_type):
                product_type_list.extend(group1)
                continue
            if group2.__contains__(j.product_type):
                product_type_list.extend(group2)
                continue
            product_type_list.append(j.product_type)
    items = compose_dao.get_compose_items(customer_id_list, product_type_list)
    if items:
        return compose_filter.filter(items, weight)
    else:
        return None