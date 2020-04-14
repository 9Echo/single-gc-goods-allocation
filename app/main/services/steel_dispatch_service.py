# -*- coding: utf-8 -*-
# Description: 钢铁配货服务
# Created: shaoluyu 2020/03/12
import copy

from app.main.entity.delivery_sheet import DeliverySheet
from app.main.entity.load_task import LoadTask
from app.main.entity.stock import Stock
from app.main.services import stock_service
from app.task.pulp_task.analysis.rules import pulp_solve
from model_config import ModelConfig


def dispatch():
    """
    车辆配货
    :param :
    :return:
    """
    # 根据车辆条件获取库存
    city_stock_list_dict = dict()
    result = list()
    stock_list = stock_service.deal_stock()
    for i in stock_list:
        city_stock_list_dict.setdefault(i.CITY, []).append(i)
    # 过滤库存，调用算法进行配货
    for k, v in city_stock_list_dict.items():
        load_task_list = goods_filter(k, v)
        result.extend(load_task_list)
    return result


def goods_filter(city, stock_list):
    """
    货物按照逾期时间倒序排序，选出第一个
    1 选出与第一个同一收货地的数据，并且出库仓库不超过两个
    if 有数据：
        将数据进行背包，约束条件有重量、件数，价值是重量
    else:
        选出与第一个同一出库仓库的数据，并且收货地址不超过两个
        if 有数据：
            将数据进行背包，约束条件有重量、件数，价值是重量
        else:
            将stock_list去除第一个，回到第一步操作，以此类推
    :param city:
    :param stock_list:
    :return:
    """
    load_task_id = 0
    # 数据格式处理，进行背包处理
    result = []
    while stock_list:
        weight_list = []
        for i in stock_list:
            weight_list.append(i.CANSENDWEIGHT)
        value_list = copy.deepcopy(weight_list)
        result_index_list = pulp_solve.pulp_pack(weight_list, None, value_list, ModelConfig.RG_MAX_WEIGHT)
        load_task = LoadTask()
        for i in result_index_list:
            load_task.city = city
            load_task_id += 1
            load_task.load_task_id = city + str(load_task_id)
            load_task.weight += stock_list[i].CANSENDWEIGHT
            load_task.items.append(stock_list[i])
        result.append(load_task)
        for i in result_index_list:
            stock_list.pop(i)
    # 数据返回
    return result


if __name__ == '__main__':
    dispatch()
