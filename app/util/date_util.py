# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 15:38
# @Author  : Zihao.Liu
from datetime import datetime


def get_now_str():
    """获取当前时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")