# -*- coding: utf-8 -*-
# Description: 钢铁配货服务
# Created: shaoluyu 2020/03/12
import copy
import math
from typing import List

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
    end_point_stock_list_dict = dict()
    result = list()
    stock_list = stock_service.deal_stock()
    print('今日0点总库存:' + str(sum(i.CANSENDWEIGHT for i in stock_list)) + 'kg')
    for i in stock_list:
        end_point_stock_list_dict.setdefault(i.end_point, []).append(i)
    # 过滤库存，调用算法进行配货
    for k, v in end_point_stock_list_dict.items():
        load_task_list = goods_filter(k, v)
        result.extend(load_task_list)
    return result


def goods_filter(end_point, stock_list):
    """
    :param end_point:
    :param stock_list:
    :return:
    """
    surplus_list = []
    load_task_result = []
    name_stock_list_dict = dict()
    for stock in stock_list:
        name_stock_list_dict.setdefault(stock.prod_kind_price_out, []).append(stock)
    for prod, prod_stock_list in name_stock_list_dict.items():
        while prod_stock_list:
            weight_list = ([item.CANSENDWEIGHT for item in prod_stock_list])
            value_list = copy.deepcopy(weight_list)
            result_index_list = pulp_solve.pulp_pack(weight_list, None, value_list, ModelConfig.RG_MAX_WEIGHT)
            if ModelConfig.RG_MAX_WEIGHT - 1000 <= sum([prod_stock_list[r].CANSENDWEIGHT for r in result_index_list]) \
                    <= ModelConfig.RG_MAX_WEIGHT:
                load_task = LoadTask()
                for index in sorted(result_index_list, reverse=True):
                    load_task.city = prod_stock_list[index].CITY
                    load_task.end_point = end_point
                    load_task.weight += prod_stock_list[index].CANSENDWEIGHT
                    load_task.items.append(prod_stock_list[index])
                    prod_stock_list.pop(index)
                load_task_result.append(load_task)
            else:
                break
        if prod_stock_list:
            surplus_list.extend(prod_stock_list)
    load_task_result.extend(limit_stock(surplus_list))
    # 数据返回
    return load_task_result


def limit_stock(stock_list):
    load_task_list = []
    while stock_list:
        stock_list.sort(key=lambda x: x.end_point)
        total_weight = 0
        load_task = LoadTask()
        load_task_list.append(load_task)
        for i in copy.copy(stock_list):
            total_weight += i.CANSENDWEIGHT
            if total_weight <= ModelConfig.RG_MAX_WEIGHT:
                load_task.items.append(i)
                load_task.end_point = i.end_point
                load_task.weight += i.CANSENDWEIGHT
                stock_list.remove(i)
                if total_weight > ModelConfig.RG_MAX_WEIGHT - 500:
                    break
            else:
                item, new_item = split_item(i, total_weight - ModelConfig.RG_MAX_WEIGHT)
                if item.CANSENDWEIGHT > 0:
                    load_task.items.append(item)
                    load_task.end_point = i.end_point
                    load_task.weight += i.CANSENDWEIGHT
                stock_list.remove(item)
                stock_list.insert(0, new_item)
                break
    return load_task_list


def split_item(item: Stock, delta_weight):
    """

    :param item:
    :param delta_weight:
    :return:
    """
    new_cunt = math.ceil(delta_weight / item.CANSENDWEIGHT * item.CANSENDNUMBER)
    new_weight = new_cunt * (item.CANSENDWEIGHT / item.CANSENDNUMBER)

    new_item = copy.deepcopy(item)
    new_item.CANSENDWEIGHT = new_weight
    new_item.CANSENDNUMBER = new_cunt
    item.CANSENDWEIGHT = item.CANSENDWEIGHT - new_weight
    item.CANSENDNUMBER = item.CANSENDNUMBER - new_cunt
    return item, new_item


if __name__ == '__main__':
    result = dispatch()
    stad_list = list(filter(lambda x: x.weight > 30000, result))
    print(len(stad_list))
