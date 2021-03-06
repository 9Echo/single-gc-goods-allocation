from typing import List, Dict
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.main.steel_factory.rule.goods_filter_rule import goods_filter
from app.main.steel_factory.rule.split_rule import split
from app.util.enum_util import DispatchType, LoadTaskType
from app.util.get_weight_limit import get_lower_limit
from model_config import ModelConfig


def layer_filter(stock_list: List, stock_dict: Dict, truck: Truck):
    """
    按层次分货
    第一层：一装一卸
    第二层：同库两装一卸
    第三层：异库两装一卸
    第四层：一装两卸
    """
    max_weight = truck.load_weight
    # 车次对象
    load_task = None
    tail_list = stock_dict['tail']
    huge_list = stock_dict['huge']
    # 先跟tail_list执行拼货
    for i in stock_list:
        if truck.big_commodity_name and i.big_commodity_name != truck.big_commodity_name:
            continue
        if i.actual_weight > (max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT):
            continue
        # 一装一卸
        load_task = first_deal_general_stock(tail_list, i, DispatchType.SECOND, max_weight)
        if load_task:
            break
        # 同区两装一卸
        load_task = second_deal_general_stock(tail_list, i, DispatchType.SECOND, max_weight)
        if load_task:
            break
        # 一装两卸
        load_task = fourth_deal_general_stock(tail_list, i, DispatchType.SECOND, max_weight)
        if load_task:
            break
        # 在跟huge_list执行拼货
        # 一装一卸
        load_task = first_deal_general_stock(huge_list, i, DispatchType.SECOND, max_weight)
        if load_task:
            break
        # 同区两装一卸
        load_task = second_deal_general_stock(huge_list, i, DispatchType.SECOND, max_weight)
        if load_task:
            break
        # 一装两卸
        load_task = fourth_deal_general_stock(huge_list, i, DispatchType.SECOND, max_weight)
        if load_task:
            break
    # 合并
    merge_result(load_task)
    return load_task


def first_deal_general_stock(stock_list, i, dispatch_type, max_weight):
    """
    一装一卸筛选器
    :param i:
    :param max_weight:
    :param stock_list:
    :param dispatch_type:
    :return:
    """
    # 取第i个元素作为目标库存
    temp_stock = i
    # 拆散的情况下，最大重量等于车辆最大载重，下浮1000
    if dispatch_type is DispatchType.THIRD:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT
        new_min_weight = surplus_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT
    # 如果拉标载
    elif get_lower_limit(temp_stock.big_commodity_name) <= max_weight <= ModelConfig.RG_MAX_WEIGHT:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = get_lower_limit(temp_stock.big_commodity_name) - temp_stock.actual_weight
    # 不拉标载，最小重量等于车辆最大载重扣除目标货物的重量，下浮2000
    else:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = max_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT - temp_stock.actual_weight
    # 得到待匹配列表
    filter_list = [stock for stock in stock_list if stock is not temp_stock
                   and stock.deliware_house == temp_stock.deliware_house
                   and stock.standard_address == temp_stock.standard_address
                   and stock.piece_weight <= surplus_weight
                   ]
    # 如果卷重小于24或者大于29，则不拼线材
    if temp_stock.big_commodity_name == '老区-卷板' and (
            temp_stock.actual_weight >= ModelConfig.RG_J_MIN_WEIGHT or
            temp_stock.actual_weight < ModelConfig.RG_SECOND_MIN_WEIGHT):
        filter_list = [stock_j for stock_j in filter_list if stock_j.big_commodity_name == '老区-卷板']
    if filter_list:
        for i in range(len(filter_list)):
            temp_filter_list = filter_list[:i + 1]
            if temp_stock.big_commodity_name == '老区-型钢':
                temp_max_weight: int = 0
                # 目标拼货组合
                target_compose_list: List[Stock] = list()
                temp_set: set = set([i.specs for i in temp_filter_list])
                for i in temp_set:
                    temp_list = [v for v in temp_filter_list if v.specs == i or v.specs == temp_stock.specs]
                    result_list = split(temp_list)
                    # 选中的列表
                    compose_list, value = goods_filter(result_list, surplus_weight)
                    if value >= new_min_weight:
                        if temp_max_weight < value:
                            temp_max_weight = value
                            target_compose_list = compose_list
                if temp_max_weight:
                    temp_stock = temp_stock if dispatch_type is not DispatchType.THIRD else None
                    if temp_stock:
                        target_compose_list.append(temp_stock)
                    return create_load_task(target_compose_list, None, LoadTaskType.TYPE_1.value)
            else:
                temp_list = split(temp_filter_list)
                # 选中的列表
                compose_list, value = goods_filter(temp_list, surplus_weight)
                if value >= new_min_weight:
                    temp_stock = temp_stock if dispatch_type is not DispatchType.THIRD else None
                    if temp_stock:
                        compose_list.append(temp_stock)
                    return create_load_task(compose_list, None, LoadTaskType.TYPE_1.value)
    # 一单在达标重量之上并且无货可拼的情况生成车次
    elif new_min_weight <= 0:
        return create_load_task([temp_stock], None, LoadTaskType.TYPE_1.value)
    else:
        return None


def second_deal_general_stock(stock_list, i, dispatch_type, max_weight):
    """
    两装一卸（同区仓库）筛选器
    :param max_weight:
    :param i:
    :param stock_list:
    :param dispatch_type:
    :return:
    """
    # 取第i个元素作为目标库存
    temp_stock = i
    # 拆散的情况下，最大重量等于车辆最大载重，下浮1000
    if dispatch_type is DispatchType.THIRD:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT
        new_min_weight = surplus_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT
    # 如果拉标载
    elif get_lower_limit(temp_stock.big_commodity_name) <= max_weight <= ModelConfig.RG_MAX_WEIGHT:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = get_lower_limit(temp_stock.big_commodity_name) - temp_stock.actual_weight
    # 不拉标载，最大重量等于车辆最大载重扣除目标货物的重量，下浮2000
    else:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = max_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT - temp_stock.actual_weight
    # 获取可拼货同区仓库
    warehouse_out_group = get_warehouse_out_group(temp_stock)
    # 条件筛选
    filter_list = [stock for stock in stock_list if stock is not temp_stock
                   and stock.standard_address == temp_stock.standard_address
                   and stock.deliware_house in warehouse_out_group
                   and stock.piece_weight <= surplus_weight]
    optimal_weight, target_compose_list = get_optimal_group(filter_list, temp_stock, surplus_weight, new_min_weight,
                                                            'deliware_house')
    if optimal_weight:
        temp_stock = temp_stock if dispatch_type is not DispatchType.THIRD else None
        if temp_stock:
            target_compose_list.append(temp_stock)
        return create_load_task(target_compose_list, None, LoadTaskType.TYPE_2.value)
    else:
        return None


def fourth_deal_general_stock(stock_list, i, dispatch_type, max_weight):
    """
    一装两卸筛选器
    :param max_weight:
    :param i:
    :param stock_list:
    :param dispatch_type:
    :return:
    """
    # 取第i个元素作为目标库存
    temp_stock = i
    # 拆散的情况下，最大重量等于车辆最大载重，下浮1000
    if dispatch_type is DispatchType.THIRD:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT
        new_min_weight = surplus_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT
    # 如果拉标载
    elif get_lower_limit(temp_stock.big_commodity_name) <= max_weight <= ModelConfig.RG_MAX_WEIGHT:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = get_lower_limit(temp_stock.big_commodity_name) - temp_stock.actual_weight
    # 不拉标载，最大重量等于车辆最大载重扣除目标货物的重量，下浮2000
    else:
        surplus_weight = max_weight + ModelConfig.RG_SINGLE_UP_WEIGHT - temp_stock.actual_weight
        new_min_weight = max_weight - ModelConfig.RG_SINGLE_LOWER_WEIGHT - temp_stock.actual_weight
    filter_list = [stock for stock in stock_list if stock is not temp_stock
                   and stock.deliware_house == temp_stock.deliware_house
                   and stock.actual_end_point == temp_stock.actual_end_point
                   and stock.piece_weight <= surplus_weight]
    optimal_weight, target_compose_list = get_optimal_group(filter_list, temp_stock, surplus_weight, new_min_weight,
                                                            'standard_address')
    if optimal_weight:
        if temp_stock:
            target_compose_list.append(temp_stock)
        return create_load_task(target_compose_list, None, LoadTaskType.TYPE_4.value)
    else:
        return None


def get_optimal_group(filter_list, temp_stock, surplus_weight, new_min_weight, attr_name):
    """
    获取最优组别
    :param attr_name:
    :param filter_list:
    :param temp_stock:
    :param surplus_weight:
    :param new_min_weight:
    :return:
    """
    # 如果卷重小于24或者大于29，则不拼线材
    if temp_stock.big_commodity_name == '老区-卷板' and (
            temp_stock.actual_weight >= ModelConfig.RG_J_MIN_WEIGHT or
            temp_stock.actual_weight <= ModelConfig.RG_SECOND_MIN_WEIGHT):
        filter_list = [stock_j for stock_j in filter_list if stock_j.big_commodity_name == '老区-卷板']
    if not filter_list:
        return 0, []
    for item in range(len(filter_list)):
        temp_filter_list = filter_list[:item + 1]
        temp_max_weight: int = 0
        # 目标拼货组合
        target_compose_list: List[Stock] = list()
        temp_set: set = set([getattr(i, attr_name) for i in temp_filter_list])
        # 如果目标货物品类为型钢
        if temp_stock.big_commodity_name == '老区-型钢':
            for i in temp_set:
                if i != getattr(temp_stock, attr_name):
                    temp_list = [v for v in temp_filter_list if
                                 getattr(v, attr_name) == i or getattr(v, attr_name) == getattr(temp_stock, attr_name)]
                    # 获取规格信息
                    spec_set = set([j.specs for j in temp_list])
                    for spec in spec_set:
                        xg_list = [v for v in temp_list if v.specs == temp_stock.specs or v.specs == spec]
                        result_list = split(xg_list)
                        # 选中的列表
                        compose_list, value = goods_filter(result_list, surplus_weight)
                        if value >= new_min_weight:
                            if temp_max_weight < value:
                                temp_max_weight = value
                                target_compose_list = compose_list
        else:
            for i in temp_set:
                if i != getattr(temp_stock, attr_name):
                    temp_list = [v for v in temp_filter_list if
                                 getattr(v, attr_name) == i or getattr(v, attr_name) == getattr(temp_stock, attr_name)]
                    result_list = split(temp_list)
                    # 选中的列表
                    compose_list, value = goods_filter(result_list, surplus_weight)
                    if value >= new_min_weight:
                        if temp_max_weight < value:
                            temp_max_weight = value
                            target_compose_list = compose_list
        if temp_max_weight:
            return temp_max_weight, target_compose_list
    return 0, []


def get_warehouse_out_group(temp_stock: Stock) -> List[str]:
    for group in ModelConfig.RG_WAREHOUSE_GROUP:
        if temp_stock.deliware_house in group:
            return group


def merge_result(load_task):
    if load_task:
        result_dict = dict()
        for item in load_task.items:
            result_dict.setdefault(item.parent_load_task_id, []).append(item)
        # 暂时清空items
        load_task.items = []
        for res_list in result_dict.values():
            sum_list = [(i.weight, i.count) for i in res_list]
            sum_weight = sum(i[0] for i in sum_list)
            sum_count = sum(i[1] for i in sum_list)
            res_list[0].weight = round(sum_weight, 3)
            res_list[0].count = sum_count
            load_task.items.append(res_list[0])
    else:
        return None
