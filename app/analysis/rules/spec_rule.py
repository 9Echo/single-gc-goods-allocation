# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:17
# @Author  : Zihao.Liu
from app.main.entity.order import Order


def spec_filter(order: Order, stocks: list):
    """
    规格过滤规则
    :param stocks: 库存
    :return:
    """
    return stocks