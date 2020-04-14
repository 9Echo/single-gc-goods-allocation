# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12

"""
库存管理局限：
1、库存来源是日钢中间库，每20分钟可获取最新库存，并且库存信息跟实际库存有误差
2、没有修改库存的权限
"""
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


def deal_stock():
    """
    处理库存数据 将数据都分为32吨及以下的标准
    Args:

    Returns:

    Raise:

    """
    deal_data = []
    stock_list = get_stock()
    for stock in stock_list:
        try:
            if float(stock.CANSENDWEIGHT) <= 32.0:
                stock.CANSENDWEIGHT = int(round(float(stock.CANSENDWEIGHT) * 1000))
                stock.CANSENDNUMBER = int(stock.CANSENDNUMBER)
                deal_data.append(stock)
            else:
                CANSENDNUMBER = float(stock.CANSENDNUMBER)
                CANSENDWEIGHT = float(stock.CANSENDWEIGHT) * 1000
                # 件重
                per_weight = CANSENDWEIGHT / CANSENDNUMBER
                # 32吨最多能有几件向下取整
                num = 32000 // per_weight
                stock_copy = copy.deepcopy(stock)
                # CANSENDNUMBER一共可以分几组
                if num == 0:
                    continue
                group_num = int(CANSENDNUMBER // num)
                # 余数
                remainder = CANSENDNUMBER % num
                stock_copy.CANSENDWEIGHT = int(round(per_weight * num))
                stock_copy.CANSENDNUMBER = int(num)
                if group_num > 0:
                    for i in range(group_num):
                        deal_data.append(stock_copy)
                stock_copy.CANSENDWEIGHT = int(round(per_weight * remainder))
                stock_copy.CANSENDNUMBER = int(remainder)
                deal_data.append(stock_copy)
        except Exception as e:
            traceback.print_exc(e)
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


data = deal_stock()
print(data)
