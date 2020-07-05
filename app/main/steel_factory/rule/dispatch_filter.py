# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 14:03
# @Author  : Zihao.Liu
import copy
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.main.steel_factory.rule.layer_filter_rule import layer_filter
from app.util.enum_util import DispatchType, LoadTaskType
from app.util.generate_id import TrainId
from model_config import ModelConfig


def dispatch_filter(load_task_list, stock_list):
    """
    分货规则
    :param load_task_list:
    :param stock_list:
    :param xg_dict:
    :return:
    """
    # 甩货列表
    surplus_stock_dict = dict()
    # 转换字典
    stock_dict = {i.stock_id: i for i in stock_list}
    # 优先考虑急发特殊货物
    general_stock_dict = layer_filter(stock_dict, load_task_list, DispatchType.FIRST, ModelConfig.RG_MIN_WEIGHT)
    # 剩余优先考虑急发特殊货物生成车次，走29吨包车运输
    for k, v in copy.copy(general_stock_dict).items():
        if v.sort == 1:
            load_task_list.append(create_load_task([v], TrainId.get_id(), LoadTaskType.TYPE_1.value))
            general_stock_dict.pop(k)
    # 剩余货物走正常流程
    if general_stock_dict:
        # 目标货物整体分
        first_surplus_stock_dict = layer_filter(general_stock_dict, load_task_list, DispatchType.SECOND,
                                                ModelConfig.RG_MIN_WEIGHT)
        # 目标货物拆散分
        surplus_stock_dict = layer_filter(first_surplus_stock_dict, load_task_list, DispatchType.THIRD,
                                          ModelConfig.RG_MIN_WEIGHT)
    return surplus_stock_dict
