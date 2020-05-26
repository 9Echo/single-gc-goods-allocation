# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 14:03
# @Author  : Zihao.Liu
import copy
from typing import Dict, List
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.main.steel_factory.rule.goods_filter_rule import goods_filter
from app.main.steel_factory.rule.layer_filter_rule import layer_filter
from app.util.enum_util import DispatchType, LoadTaskType
from app.util.generate_id import TrainId
from model_config import ModelConfig


def dispatch_filter(load_task_list, stock_list):
    # 甩货列表
    surplus_stock_dict = dict()
    # 优先考虑的货物列表
    prioritize_list: List[Stock] = list()
    # 剩余货物列表
    surplus_list: List[Stock] = list()
    # 分类
    for i in stock_list:
        if i.piece_weight >= ModelConfig.RG_SECOND_MIN_WEIGHT and i.priority in [1, 2]:
            prioritize_list.append(i)
        else:
            surplus_list.append(i)

    # 标载车次列表
    standard_stock_list = list(filter(lambda x: x.actual_weight >= ModelConfig.RG_MIN_WEIGHT, stock_list))
    # 普通车次列表
    general_stock_list = list(filter(lambda x: x.actual_weight < ModelConfig.RG_MIN_WEIGHT, stock_list))
    # 标载车次拼凑一装一卸小件货物
    for standard_stock in standard_stock_list:
        # 可拼车列表
        compose_list = list()
        # 车次剩余载重
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - standard_stock.actual_weight
        # 筛选符合拼车条件的库存列表
        filter_list = list(filter(lambda x: x.deliware_house == standard_stock.deliware_house
                                            and x.standard_address == standard_stock.standard_address
                                            and x.actual_weight <= surplus_weight
                                            and x.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(
            standard_stock.big_commodity_name), general_stock_list))
        # 如果有，按照surplus_weight为约束进行匹配
        if filter_list:
            compose_list, value = goods_filter(filter_list, surplus_weight)
            for stock in compose_list:
                general_stock_list.remove(stock)
        # 生成车次数据
        load_task_list.extend(
            create_load_task(compose_list + [standard_stock], TrainId.get_id(), LoadTaskType.TYPE_1.value))
    if general_stock_list:
        general_stock_dict: Dict[int, Stock] = dict()
        for i in general_stock_list:
            general_stock_dict[i.stock_id] = i
        first_surplus_stock_dict = layer_filter(general_stock_dict, load_task_list, DispatchType.FIRST,
                                                ModelConfig.RG_MIN_WEIGHT)
        surplus_stock_dict = layer_filter(first_surplus_stock_dict, load_task_list, DispatchType.SECOND,
                                          ModelConfig.RG_MIN_WEIGHT)
    return surplus_stock_dict
