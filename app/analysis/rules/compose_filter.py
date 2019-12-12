# -*- coding: utf-8 -*-
# @Time    : 2019/12/12
# @Author  : shaoluyu
from app.analysis.rules import package_solution


def filter(delivery_items: list, weight):
    """重量过滤规则：
    1.总重量不超过35吨
    2.对所有订单项进行拼货使其尽量接近40吨
    """
    filtered_items = []
    weight_cost = []
    # 根据item的重量生成weight_cost的列表
    for item in delivery_items:
        weight_cost.append(tuple([item.get('weight'), item.get('weight')]))
    final_weight, result_list = package_solution.dynamic_programming(len(delivery_items), 35000-weight, weight_cost)
    print(result_list)
    for i in range(0, len(result_list)):
        if result_list[i] == 1:
            filtered_items.append(delivery_items[i])
    return filtered_items