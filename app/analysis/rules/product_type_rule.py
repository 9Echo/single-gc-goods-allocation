# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:19
# @Author  : Zihao.Liu


def filter(delivery_items: list):
    """
    产品类型过滤规则
    """
    filtered_items = []
    # 将产品品类分组，属于group1或group2的可以分到同一单，其余的每个品类各一单
    group1 = ['热镀', '热度', '热镀1', 'QF热镀管']
    group2 = ['焊管', '焊管 ','焊管1']
    target_group = None
    for item in delivery_items:
        if group1.__contains__(item.product_type):
            target_group = group1
            break
        if group2.__contains__(item.product_type):
            target_group = group2
            break
    if target_group is None:
        # 订单中没有属于分组内的产品时
        filtered_items.append(delivery_items[0])
    else:
        for item in delivery_items[:]:
            if target_group.__contains__(item.product_type):
                filtered_items.append(item)
    return filtered_items




