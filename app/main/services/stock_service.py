# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12

"""
库存管理局限：
1、库存来源是日钢中间库，每20分钟可获取最新库存，并且库存信息跟实际库存有误差
2、没有修改库存的权限
"""
from typing import List

from app.main.dao.stock_dao import select_stock
from app.main.entity.stock import Stock
import copy
import traceback


def get_stock():
    """
    根据车辆属性获取库存
    包括，城市、区县、品种、是否运输外库
    :param vehicle:
    :return: 库存
    """
    """
    步骤：
    提取车辆条件
    提取redis中保存的库存
    筛选库存并返回
    
    """
    # 获取库存
    datas = select_stock()
    # 存放库存信息
    stock_list = []
    for data in datas:
        stock = Stock(data)
        stock_list.append(stock)
    return stock_list


def deal_stock() -> List[Stock]:
    """
    处理库存数据 将数据都分为32吨及以下的标准
    Args:

    Returns:

    Raise:

    """
    deal_data = []
    stock_list = get_stock()
    for stock in stock_list:
        # 将str的件数转化为整数
        CANSENDNUMBER = int(stock.CANSENDNUMBER)
        # 将str的可发重量先转化为浮点型*1000在四舍五入后转为整数 千克
        CANSENDWEIGHT = int(round(float(stock.CANSENDWEIGHT) * 1000))
        if float(stock.CANSENDWEIGHT) <= 32.0:
            stock_copy = copy.deepcopy(stock)
            stock_copy.CANSENDWEIGHT = CANSENDWEIGHT
            stock_copy.CANSENDNUMBER = CANSENDNUMBER
            deal_data.append(stock_copy)
        else:
            # 件重是千克单位
            per_weight = CANSENDWEIGHT / CANSENDNUMBER
            # 32吨最多能有几件向下取整
            num = 32000 // per_weight
            if num == 0:
                continue
            # CANSENDNUMBER一共可以分几组
            group_num = int(CANSENDNUMBER // num)
            # 余数
            remainder = CANSENDNUMBER % num
            if group_num > 0:
                for j in range(group_num):
                    stock_copy = copy.deepcopy(stock)
                    stock_copy.CANSENDWEIGHT = int(round(per_weight * num))
                    stock_copy.CANSENDNUMBER = int(num)
                    deal_data.append(stock_copy)
            if remainder == 0:
                continue
            stock_copy = copy.deepcopy(stock)
            stock_copy.CANSENDWEIGHT = int(round(per_weight * remainder))
            stock_copy.CANSENDNUMBER = int(remainder)
            deal_data.append(stock_copy)
    return deal_data


def subtract_stock(goods_list):
    """
    扣减redis库存
    :param goods_list:
    :return:
    """


def restore_stock(goods_list):
    """
    还原redis库存
    :param goods_list:
    :return:
    """


def update_stock_task():
    """
    定时更新redis库存，时间间隔20分钟，或监听最新库存刷新
    :return:
    """
    """
    if中间表方式获取库存：
    设定每小时预估库存刷新完毕的时间点
    将库存覆盖到redis
    if消息队列方式：
    监听订阅库存消息
    将库存覆盖到redis
    """


deal_stock()
