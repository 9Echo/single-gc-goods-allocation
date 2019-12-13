# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:15
# @Author  : Zihao.Liu

from app.analysis.rules import package_solution
from app.utils import weight_calculator


def filter(delivery_items: list):
    """重量过滤规则：
    1.总重量不超过35吨
    2.对所有订单项进行拼货使其尽量接近40吨
    """
    filtered_items = []
    weight_cost = []
    # 根据item的重量生成weight_cost的列表
    for item in delivery_items:
        # 如果出现重量为0，则该重量为0的单成一单
        if item.weight == 0:
            filtered_items.append(item)
            return filtered_items
        weight_cost.append((item.weight, item.weight))
    final_weight, result_list = package_solution.dynamic_programming(len(delivery_items), 35000, weight_cost)
    for i in range(0, len(result_list)):
        if result_list[i] == 1:
            filtered_items.append(delivery_items[i])
    return filtered_items
