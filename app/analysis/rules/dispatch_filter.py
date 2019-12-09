# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 14:03
# @Author  : Zihao.Liu
import copy

from app.analysis.rules import weight_rule


def filter(origin_order, stocks):
    """规格过滤器集合"""
    order = copy.deepcopy(origin_order)
    order = weight_rule.weight_filter(order, stocks)
    return order