import copy
from typing import Dict, List
from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule.calculate_rule import calculate
from app.main.steel_factory.rule.goods_filter_rule import goods_filter
from app.main.steel_factory.rule.split_rule import split
from app.util.enum_util import DispatchType, LoadTaskType
from model_config import ModelConfig


def layer_filter(general_stock_dict, load_task_list, dispatch_type, min_weight):
    """

    :param min_weight:
    :param general_stock_dict:
    :param load_task_list:
    :param dispatch_type:
    :return:
    """
    first_result_dict = first_deal_general_stock(general_stock_dict, load_task_list, dispatch_type, min_weight)
    second_result_dict = second_deal_general_stock(first_result_dict, load_task_list, dispatch_type, min_weight)
    third_stock_dict = third_deal_general_stock(second_result_dict, load_task_list, dispatch_type, min_weight)
    surplus_stock_dict = fourth_deal_general_stock(third_stock_dict, load_task_list, dispatch_type, min_weight)
    return surplus_stock_dict


def first_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask], dispatch_type,
                             min_weight) -> Dict[int, Stock]:
    """
    一装一卸筛选器
    :param min_weight:
    :param dispatch_type:
    :param general_stock_dict:
    :param load_task_list:
    :return:
    """
    result_dict = dict()
    while general_stock_dict:
        # 取第一个
        stock_id = list(general_stock_dict.keys())[0]
        temp_stock = general_stock_dict.get(stock_id)
        if dispatch_type is DispatchType.FIRST and temp_stock.sort != 1:
            result_dict = {**result_dict, **general_stock_dict}
            break
        # 约束
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if
                       v.deliware_house == temp_stock.deliware_house and v.standard_address == temp_stock.standard_address
                       and v.piece_weight <= surplus_weight
                       and v.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.big_commodity_name)}
        if filter_dict:
            temp_list = split(filter_dict)
            # 选中的列表
            compose_list, value = goods_filter(temp_list, surplus_weight)
            if dispatch_type is DispatchType.FIRST or dispatch_type is DispatchType.SECOND:
                if (value + temp_stock.actual_weight) >= min_weight:
                    calculate(compose_list, general_stock_dict, load_task_list, temp_stock, LoadTaskType.TYPE_1.value)
                    continue
            else:
                if value >= min_weight:
                    calculate(compose_list, general_stock_dict, load_task_list, None, LoadTaskType.TYPE_1.value)
                    continue
        general_stock_dict.pop(stock_id, 404)
        result_dict[stock_id] = temp_stock
    return result_dict


def second_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask], dispatch_type,
                              min_weight) -> Dict[int, Stock]:
    """
    两装一卸（同区仓库）筛选器
    :param min_weight:
    :param dispatch_type:
    :param general_stock_dict:
    :param load_task_list:
    :return:
    """
    result_dict = dict()
    while general_stock_dict:
        # 取第一个
        stock_id = list(general_stock_dict.keys())[0]
        temp_stock = general_stock_dict.get(stock_id)
        if dispatch_type is DispatchType.FIRST and temp_stock.sort != 1:
            result_dict = {**result_dict, **general_stock_dict}
            break
        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        warehouse_out_group: List[str] = list()
        for group in ModelConfig.RG_WAREHOUSE_GROUP:
            if temp_stock.deliware_house in group:
                warehouse_out_group = group
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if v.standard_address == temp_stock.standard_address
                       and v.deliware_house in warehouse_out_group
                       and v.piece_weight <= surplus_weight
                       and v.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.big_commodity_name)}
        if filter_dict:
            warehouse_out_list: List[str] = list()
            for i in filter_dict.values():
                if i.deliware_house not in warehouse_out_list:
                    warehouse_out_list.append(i.deliware_house)
            for warehouse_out in warehouse_out_list:
                if warehouse_out != temp_stock.deliware_house:
                    temp_dict = {k: v for k, v in filter_dict.items() if
                                 v.deliware_house == warehouse_out or v.deliware_house == temp_stock.deliware_house}
                    temp_list = split(temp_dict)
                    # 选中的列表
                    compose_list, value = goods_filter(temp_list, surplus_weight)
                    if dispatch_type is DispatchType.FIRST or dispatch_type is DispatchType.SECOND:
                        if (value + temp_stock.actual_weight) >= min_weight:
                            calculate(compose_list, general_stock_dict, load_task_list, temp_stock,
                                      LoadTaskType.TYPE_2.value)
                            is_error = False
                            break
                    else:
                        if value >= min_weight:
                            calculate(compose_list, general_stock_dict, load_task_list, None,
                                      LoadTaskType.TYPE_2.value)
                            is_error = False
                            break
        if is_error:
            general_stock_dict.pop(stock_id, 404)
            result_dict[stock_id] = temp_stock
    return result_dict


def third_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask], dispatch_type,
                             min_weight) -> Dict[int, Stock]:
    """
    两装一卸（非同区仓库）筛选器
    :param min_weight:
    :param dispatch_type:
    :param general_stock_dict:
    :param load_task_list:
    :return:
    """
    result_dict = dict()
    while general_stock_dict:
        # 取第一个
        stock_id = list(general_stock_dict.keys())[0]
        temp_stock = general_stock_dict.get(stock_id)
        if dispatch_type is DispatchType.FIRST and temp_stock.sort != 1:
            result_dict = {**result_dict, **general_stock_dict}
            break
        # 拆分成件的stock列表
        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if v.standard_address == temp_stock.standard_address
                       and v.piece_weight <= surplus_weight
                       and v.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.big_commodity_name)}
        if filter_dict:
            warehouse_out_list: List[str] = list()
            for i in filter_dict.values():
                if i.deliware_house not in warehouse_out_list:
                    warehouse_out_list.append(i.deliware_house)
            for warehouse_out in warehouse_out_list:
                if warehouse_out != temp_stock.deliware_house:
                    temp_dict = {k: v for k, v in filter_dict.items() if
                                 v.deliware_house == warehouse_out or v.deliware_house == temp_stock.deliware_house}
                    temp_list = split(temp_dict)
                    # 选中的列表
                    compose_list, value = goods_filter(temp_list, surplus_weight)
                    if dispatch_type is DispatchType.FIRST or dispatch_type is DispatchType.SECOND:
                        if (value + temp_stock.actual_weight) >= min_weight:
                            calculate(compose_list, general_stock_dict, load_task_list, temp_stock,
                                      LoadTaskType.TYPE_3.value)
                            is_error = False
                            break
                    else:
                        if value >= min_weight:
                            calculate(compose_list, general_stock_dict, load_task_list, None,
                                      LoadTaskType.TYPE_3.value)
                            is_error = False
                            break
        if is_error:
            general_stock_dict.pop(stock_id, 404)
            result_dict[stock_id] = temp_stock
    return result_dict


def fourth_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask], dispatch_type,
                              min_weight) -> Dict[int, Stock]:
    """
    一装两卸筛选器
    :param min_weight:
    :param dispatch_type:
    :param general_stock_dict:
    :param load_task_list:
    :return:
    """
    result_dict = dict()
    while general_stock_dict:
        # 取第一个
        stock_id = list(general_stock_dict.keys())[0]
        temp_stock = general_stock_dict.get(stock_id)
        if dispatch_type is DispatchType.FIRST and temp_stock.sort != 1:
            result_dict = {**result_dict, **general_stock_dict}
            break
        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if
                       v.deliware_house == temp_stock.deliware_house and v.actual_end_point == temp_stock.actual_end_point
                       and v.piece_weight <= surplus_weight
                       and v.big_commodity_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.big_commodity_name)}
        if filter_dict:
            address_list: List[str] = list()
            for i in filter_dict.values():
                if i.standard_address not in address_list:
                    address_list.append(i.standard_address)
            for address in address_list:
                if address != temp_stock.standard_address:
                    temp_dict = {k: v for k, v in filter_dict.items() if
                                 v.standard_address == address or v.standard_address == temp_stock.standard_address}
                    temp_list = split(temp_dict)
                    # 选中的列表
                    compose_list, value = goods_filter(temp_list, surplus_weight)
                    if dispatch_type is DispatchType.FIRST or dispatch_type is DispatchType.SECOND:
                        if (value + temp_stock.actual_weight) >= min_weight:
                            calculate(compose_list, general_stock_dict, load_task_list, temp_stock,
                                      LoadTaskType.TYPE_4.value)
                            is_error = False
                            break
                    else:
                        if value >= min_weight:
                            calculate(compose_list, general_stock_dict, load_task_list, None,
                                      LoadTaskType.TYPE_4.value)
                            is_error = False
                            break
        if is_error:
            general_stock_dict.pop(stock_id, 404)
            result_dict[stock_id] = temp_stock
    return result_dict
