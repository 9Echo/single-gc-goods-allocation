# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 14:03
# @Author  : Zihao.Liu
import copy
from typing import Dict, List, Any

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule import pulp_solve
from app.util.enum_util import DispatchType, LoadTaskType
from app.util.generate_id import TrainId
from model_config import ModelConfig


def dispatch_filter(general_stock_dict, load_task_list, dispatch_type, min_weight):
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
        # 约束
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if
                       v.Warehouse_out == temp_stock.Warehouse_out and v.Standard_address == temp_stock.Standard_address
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        if filter_dict:
            temp_list = split(filter_dict)
            # 选中的列表
            compose_list, value = goods_filter(temp_list, surplus_weight)
            if dispatch_type is DispatchType.FIRST:
                if (value + temp_stock.Actual_weight) >= min_weight:
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
        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        warehouse_out_group: List[str] = list()
        for group in ModelConfig.RG_WAREHOUSE_GROUP:
            if temp_stock.Warehouse_out in group:
                warehouse_out_group = group
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if v.Standard_address == temp_stock.Standard_address
                       and v.Warehouse_out in warehouse_out_group
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        if filter_dict:
            warehouse_out_list: List[str] = list()
            for i in filter_dict.values():
                if i.Warehouse_out not in warehouse_out_list:
                    warehouse_out_list.append(i.Warehouse_out)
            for warehouse_out in warehouse_out_list:
                if warehouse_out != temp_stock.Warehouse_out:
                    temp_dict = {k: v for k, v in filter_dict.items() if
                                 v.Warehouse_out == warehouse_out or v.Warehouse_out == temp_stock.Warehouse_out}
                    temp_list = split(temp_dict)
                    # 选中的列表
                    compose_list, value = goods_filter(temp_list, surplus_weight)
                    if dispatch_type is DispatchType.FIRST:
                        if (value + temp_stock.Actual_weight) >= min_weight:
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
        # 拆分成件的stock列表

        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if v.Standard_address == temp_stock.Standard_address
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        if filter_dict:
            warehouse_out_list: List[str] = list()
            for i in filter_dict.values():
                if i.Warehouse_out not in warehouse_out_list:
                    warehouse_out_list.append(i.Warehouse_out)
            for warehouse_out in warehouse_out_list:
                if warehouse_out != temp_stock.Warehouse_out:
                    temp_dict = {k: v for k, v in filter_dict.items() if
                                 v.Warehouse_out == warehouse_out or v.Warehouse_out == temp_stock.Warehouse_out}
                    temp_list = split(temp_dict)
                    # 选中的列表
                    compose_list, value = goods_filter(temp_list, surplus_weight)
                    if dispatch_type is DispatchType.FIRST:
                        if (value + temp_stock.Actual_weight) >= min_weight:
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
        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if
                       v.Warehouse_out == temp_stock.Warehouse_out and v.Actual_end_point == temp_stock.Actual_end_point
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        if filter_dict:
            address_list: List[str] = list()
            for i in filter_dict.values():
                if i.Standard_address not in address_list:
                    address_list.append(i.Standard_address)
            for address in address_list:
                if address != temp_stock.Standard_address:
                    temp_dict = {k: v for k, v in filter_dict.items() if
                                 v.Standard_address == address or v.Standard_address == temp_stock.Standard_address}
                    temp_list = split(temp_dict)
                    # 选中的列表
                    compose_list, value = goods_filter(temp_list, surplus_weight)
                    if dispatch_type is DispatchType.FIRST:
                        if (value + temp_stock.Actual_weight) >= min_weight:
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


def calculate(compose_list: List[Stock], general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask],
              temp_stock: Any, load_task_type: str):
    """
    重量计算
    :param compose_list:
    :param general_stock_dict:
    :param load_task_list:
    :param temp_stock:
    :param load_task_type:
    :return:
    """
    temp_dict = dict()
    # 选中的stock按照stock_id分类
    for compose_stock in compose_list:
        temp_dict.setdefault(compose_stock.Stock_id, []).append(compose_stock)
    new_compose_list = list()
    if temp_stock:
        new_compose_list.append(temp_stock)
    for k, v in temp_dict.items():
        # 获取被选中的原始stock
        general_stock = general_stock_dict.get(k)
        stock = v[0]
        stock.Actual_number = len(v)
        stock.Actual_weight = len(v) * stock.Piece_weight
        new_compose_list.append(stock)
        general_stock.Actual_number -= len(v)
        general_stock.Actual_weight = general_stock.Actual_number * general_stock.Piece_weight
        if general_stock.Actual_number == 0:
            general_stock_dict.pop(k)
    # 生成车次数据
    load_task_list.extend(
        create_load_task(new_compose_list, TrainId.get_id(), load_task_type))


def goods_filter(general_stock_list: List[Stock], surplus_weight: int) -> (List[Stock], int):
    """
    背包过滤方法
    :param surplus_weight:
    :param general_stock_list:
    :return:
    """
    compose_list = list()
    weight_list = ([item.Actual_weight for item in general_stock_list])
    value_list = copy.deepcopy(weight_list)
    result_index_list, value = pulp_solve.pulp_pack(weight_list, None, value_list, surplus_weight)
    for index in sorted(result_index_list, reverse=True):
        compose_list.append(general_stock_list[index])
        general_stock_list.pop(index)
    # 数据返回
    return compose_list, value


def create_load_task(stock_list: List[Stock], load_task_id, load_task_type) -> List[LoadTask]:
    """
    车次创建方法
    :param stock_list:
    :param load_task_id:
    :param load_task_type:
    :return:
    """
    total_weight = sum(i.Actual_weight for i in stock_list)
    all_product = set([i.Big_product_name for i in stock_list])
    remark = []
    for product in all_product:
        remark += ModelConfig.RG_VARIETY_VEHICLE[product]
    remark = set(remark)
    load_task_list = list()
    for i in stock_list:
        load_task = LoadTask()
        load_task.load_task_id = load_task_id
        load_task.total_weight = total_weight / 1000
        load_task.weight = i.Actual_weight / 1000
        load_task.count = i.Actual_number
        load_task.city = i.City
        load_task.end_point = i.End_point
        load_task.commodity = i.Small_product_name
        load_task.notice_num = i.Delivery
        load_task.oritem_num = i.Order
        load_task.standard = i.specs
        load_task.sgsign = i.mark
        load_task.outstock_code = i.Warehouse_out
        load_task.instock_code = i.Warehouse_in
        load_task.load_task_type = load_task_type
        load_task.big_commodity = i.Big_product_name
        load_task.receive_address = i.Address
        load_task.remark = ",".join(remark)
        load_task.parent_load_task_id = i.Parent_stock_id
        load_task.latest_order_time = i.Latest_order_time
        # 得到翻转优先级的字典
        dic_priority = dict((val, key) for key, val in ModelConfig.RG_PRIORITY.items())
        if i.Priority not in dic_priority:
            load_task.priority = ""
        else:
            load_task.priority = dic_priority[i.Priority]
        load_task_list.append(load_task)
    return load_task_list


def split(temp_dict: Dict[int, Stock]):
    """
    拆分到单件
    :param temp_dict:
    :return:
    """
    # 拆分成件的stock列表
    temp_list: List[Stock] = list()
    for i in temp_dict.values():
        for j in range(i.Actual_number):
            copy_stock = copy.deepcopy(i)
            copy_stock.Actual_number = 1
            copy_stock.Actual_weight = i.Piece_weight
            temp_list.append(copy_stock)
    return temp_list


def merge_result(load_task_list: list):
    """合并结果中load_task_id相同的信息

    Args:
        load_task_list: load_task的列表
    Returns:

    Raise:

    """
    result_dic = {}
    priority_dic = {}
    latest_order_time_dic = {}
    last_result = []
    for task in load_task_list:
        # 整理每个车次的所有最新挂单时间
        latest_order_time_dic.setdefault(task.load_task_id, set()).add(task.latest_order_time)
        # 整理每个车次的所有优先级
        priority_dic.setdefault(task.load_task_id, set()).add(
            4 if not task.priority else ModelConfig.RG_PRIORITY[task.priority])
        # 按（车次ID，车次父ID）整理车次
        result_dic.setdefault((task.load_task_id, task.parent_load_task_id), []).append(task)
    for res in result_dic:
        # 得到车次号
        load_task_id = res[0]
        # 同一个(load_task_id,parent_load_task_id)的load_task列表
        res_list = result_dic[res]
        if len(res_list) > 1:
            sum_list = [(i.weight, i.count) for i in res_list]
            sum_weight = sum(i[0] for i in sum_list)
            sum_count = sum(i[1] for i in sum_list)
            res_list[0].weight = sum_weight
            res_list[0].count = sum_count
        res_list[0].latest_order_time = min(latest_order_time_dic[load_task_id])
        res_list[0].priority_grade = ModelConfig.RG_PRIORITY_GRADE[min(priority_dic[load_task_id])]
        last_result.append(res_list[0])
    last_result.sort(key=lambda x: (x.priority_grade, x.latest_order_time), reverse=False)
    return last_result
