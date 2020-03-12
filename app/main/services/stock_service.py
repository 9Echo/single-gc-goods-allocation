# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12

"""
库存管理局限：
1、库存来源是日钢中间库，每20分钟可获取最新库存，并且库存信息跟实际库存有误差
2、没有修改库存的权限
"""


def get_stock(vehicle):
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
