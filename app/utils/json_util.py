# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 15:58
# @Author  : Zihao.Liu


def json_encode(obj):
    """为BaseEntity提供json封装"""
    if isinstance(obj, list):
        return [item.as_dict() for item in obj]
    else:
        return obj.as_dict()