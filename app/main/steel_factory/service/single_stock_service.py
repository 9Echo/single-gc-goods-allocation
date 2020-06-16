# -*- coding: utf-8 -*-
# Description: 动态库存服务
# Created: shaoluyu 2020/06/16
from app.main.steel_factory.entity.load_task_item import LoadTaskItem
from app.main.steel_factory.entity.stock import Stock


def get_stock_id(obj):
    """
    根据库存信息生成每条库存的唯一id
    """
    if isinstance(obj, Stock):
        return hash(obj.notice_num + obj.oritem_num + obj.deliware_house)
    elif isinstance(obj, LoadTaskItem):
        return hash(obj.notice_num + obj.oritem_num + obj.outstock_code)


def get_stock():
    """
    获取当前库存
    :return:
    """
    pass


def update_stock(load_task, stock_list):
    """
    根据已开单车次明细，更新库存
    :param load_task_list:
    :return: 更新后的库存
    """
    return stock_list
