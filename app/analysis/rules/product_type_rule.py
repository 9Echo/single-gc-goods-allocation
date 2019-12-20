# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:19
# @Author  : Zihao.Liu


def filter(delivery_items: list):
    """
    产品类型过滤规则
    """
    filtered_items = []
    # 将产品品类分组，属于一个group的可以分到同一单，其余的每个品类各一单
    similar_groups = [('热镀', '热度', '热镀1'), ('焊管', '焊管 ','焊管1')]
    target_group = None
    for item in delivery_items:
        for i in range(0, len(similar_groups)):
            if similar_groups[i].__contains__(item.product_type):
                target_group = similar_groups[i]
                break
        if target_group:
            break
    if target_group is None:
        # 订单中没有属于分组内的产品时
        product_type = delivery_items[0].product_type
        for i in delivery_items:
            if i.product_type == product_type:
                filtered_items.append(i)
    else:
        for item in delivery_items[:]:
            if target_group.__contains__(item.product_type):
                filtered_items.append(item)
    return filtered_items




