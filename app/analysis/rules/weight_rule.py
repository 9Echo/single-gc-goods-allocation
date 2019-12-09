# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:15
# @Author  : Zihao.Liu
import random


def weight_filter(order, stocks: list):
    """重量过滤规则：
    1.总重量不超过40吨
    2.对所有订单项进行拼货使其尽量接近40吨
    """
    for item in order.items:
        item.weight = get_weight()


    return order


def get_weight():
    """获取一个随机的重量"""
    return random.randint(5, 15)