# -*- coding: utf-8 -*-
# Description: 钢铁配货服务
# Created: shaoluyu 2020/03/12
import copy
import pandas as pd
from typing import List, Dict
from app.main.entity.load_task import LoadTask
from app.main.entity.stock import Stock
from app.main.services import stock_service
from app.main.services import generate_excel_service
from app.task.pulp_task.analysis.rules import pulp_solve
from app.utils.generate_id import TrainId
from model_config import ModelConfig


def dispatch() -> List[LoadTask]:
    """
    车辆配货
    :param :
    :return:
    """
    """
    步骤：
    1 将单条库存数据满足标载条件[31,33]的数据直接生成车次，并搜索满足一装一卸的可拼的其他货物，拼到该车次，其中包含超期或催货标为急发车次，并且类型为一装一卸
    2 按照优先发运、最新挂单时间进行正序排序
    3 选择第一条作为目标数据，将除第一条其余数据中出库仓库和区县与其相同或卸货地址与其相同的数据筛选出来作为待选集
    4 按照优先级将待选集与目标数据利用背包进行匹配，使重量最大化，匹配成功（总量在[31,33]）生成车次，标注是否急发和类型，匹配不成功放入甩货列表，
    优先级依次为：一装一卸，两装一卸（同区仓库），两装一卸(不同区仓库),一装两卸
    """

    load_task_list = list()
    # 库存信息获取
    stock_list: List[Stock] = stock_service.deal_stock()
    # 标载车次列表
    standard_stock_list = list(
        filter(lambda x: x.Actual_weight >= ModelConfig.RG_MIN_WEIGHT, stock_list))
    # 普通车次列表
    general_stock_list = list(
        filter(lambda x: x.Actual_weight < ModelConfig.RG_MIN_WEIGHT, stock_list))
    # 标载车次拼凑一装一卸小件货物
    for standard_stock in standard_stock_list:
        # 可拼车列表
        compose_list = list()
        # 车次剩余载重
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - standard_stock.Actual_weight
        # 筛选符合拼车条件的库存列表
        filter_list = list(filter(lambda x: x.Warehouse_out == standard_stock.Warehouse_out
                                            and x.Address == standard_stock.Address
                                            and x.Actual_weight <= surplus_weight
                                            and x.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(
            standard_stock.Big_product_name), general_stock_list))
        # 如果有，按照surplus_weight为约束进行匹配
        if filter_list:
            compose_list = goods_filter(filter_list, surplus_weight)
        # 生成车次数据
        load_task_list.extend(create_load_task(compose_list + [standard_stock], TrainId.get_id(), LoadTask.type_1))
    if general_stock_list:
        general_stock_dict = dict()
        for i in general_stock_list:
            general_stock_dict[i.Stock_id] = i
        first_result_dict = first_deal_general_stock(general_stock_dict, load_task_list)
        second_result_dict = second_deal_general_stock(first_result_dict, load_task_list)
        surplus_stock_dict = third_deal_general_stock(second_result_dict, load_task_list)
        # 分不到标载车次的部分，甩掉，生成一个伪车次加明细
        if surplus_stock_dict:
            load_task_list.extend(create_load_task(list(surplus_stock_dict.values()), -1, LoadTask.type_4))
        return load_task_list


def first_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask]) -> Dict[int, Stock]:
    """
    一装一卸筛选器
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
        temp_list = list()
        # 约束
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight
        general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if
                       v.Warehouse_out == temp_stock.Warehouse_out and v.Address == temp_stock.Address
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        # 符合条件的stock拆分到临时列表
        for i in filter_dict.values():
            for j in range(i.Actual_number):
                copy_stock = copy.deepcopy(i)
                copy_stock.Actual_number = 1
                copy_stock.Actual_weight = i.Piece_weight
                temp_list.append(copy_stock)
        # 选中的列表
        compose_list = goods_filter(temp_list, surplus_weight)
        if compose_list and (
                sum(x.Actual_weight for x in compose_list) + temp_stock.Actual_weight) >= ModelConfig.RG_MIN_WEIGHT:
            temp_dict = dict()
            # 选中的stock按照stock_id分类
            for compose_stock in compose_list:
                temp_dict.setdefault(compose_stock.Stock_id, []).append(compose_stock)
            new_compose_list = list()
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
            load_task_list.extend(create_load_task(new_compose_list + [temp_stock], TrainId.get_id(), LoadTask.type_1))
        else:
            result_dict[stock_id] = temp_stock
    return result_dict


def second_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask]) -> Dict[int, Stock]:
    """
    两装一卸（同区仓库）筛选器
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
        temp_list = list()
        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight
        general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if v.Address == temp_stock.Address
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        warehouse_out_list = list()
        for i in filter_dict.values():
            if i.Warehouse_out not in warehouse_out_list:
                warehouse_out_list.append(i.Warehouse_out)
        for warehouse_out in warehouse_out_list:
            if warehouse_out != temp_stock.Warehouse_out:
                temp_dict = {k: v for k, v in filter_dict.items() if
                             v.Warehouse_out == warehouse_out or v.Warehouse_out == temp_stock.Warehouse_out}
                for i in temp_dict.values():
                    for j in range(i.Actual_number):
                        copy_stock = copy.deepcopy(i)
                        copy_stock.Actual_number = 1
                        copy_stock.Actual_weight = i.Piece_weight
                        temp_list.append(copy_stock)
                # 选中的列表
                compose_list = goods_filter(temp_list, surplus_weight)
                if compose_list and (
                        sum(x.Actual_weight for x in
                            compose_list) + temp_stock.Actual_weight) >= ModelConfig.RG_MIN_WEIGHT:
                    temp_dict = dict()
                    # 选中的stock按照stock_id分类
                    for compose_stock in compose_list:
                        temp_dict.setdefault(compose_stock.Stock_id, []).append(compose_stock)
                    new_compose_list = list()
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
                        create_load_task(new_compose_list + [temp_stock], TrainId.get_id(), LoadTask.type_3))
                    is_error = False
                    break
        if is_error:
            result_dict[stock_id] = temp_stock
    return result_dict


def third_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask]) -> Dict[int, Stock]:
    """
    一装两卸筛选器
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
        temp_list = list()
        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight
        general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if
                       v.Warehouse_out == temp_stock.Warehouse_out and v.End_point == temp_stock.End_point
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        address_list = list()
        for i in filter_dict.values():
            if i.Address not in address_list:
                address_list.append(i.Address)
        for address in address_list:
            if address != temp_stock.Address:
                temp_dict = {k: v for k, v in filter_dict.items() if
                             v.Address == address or v.Address == temp_stock.Address}
                for i in temp_dict.values():
                    for j in range(i.Actual_number):
                        copy_stock = copy.deepcopy(i)
                        copy_stock.Actual_number = 1
                        copy_stock.Actual_weight = i.Piece_weight
                        temp_list.append(copy_stock)
                # 选中的列表
                compose_list = goods_filter(temp_list, surplus_weight)
                if compose_list and (
                        sum(x.Actual_weight for x in
                            compose_list) + temp_stock.Actual_weight) >= ModelConfig.RG_MIN_WEIGHT:
                    temp_dict = dict()
                    # 选中的stock按照stock_id分类
                    for compose_stock in compose_list:
                        temp_dict.setdefault(compose_stock.Stock_id, []).append(compose_stock)
                    new_compose_list = list()
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
                        create_load_task(new_compose_list + [temp_stock], TrainId.get_id(), LoadTask.type_2))
                    is_error = False
                    break
        if is_error:
            result_dict[stock_id] = temp_stock
    return result_dict


def goods_filter(general_stock_list: List[Stock], surplus_weight: int) -> List[Stock]:
    """
    背包过滤方法
    :param surplus_weight:
    :param general_stock_list:
    :return:
    """
    compose_list = list()
    weight_list = ([item.Actual_weight for item in general_stock_list])
    value_list = copy.deepcopy(weight_list)
    result_index_list = pulp_solve.pulp_pack(weight_list, None, value_list, surplus_weight)
    for index in sorted(result_index_list, reverse=True):
        compose_list.append(general_stock_list[index])
        general_stock_list.pop(index)
    # 数据返回
    return compose_list


def create_load_task(stock_list: List[Stock], load_task_id, load_task_type) -> List[LoadTask]:
    """
    车次创建方法
    :param stock_list:
    :param load_task_id:
    :param load_task_type:
    :return:
    """
    total_weight = sum(i.Actual_weight for i in stock_list)
    if total_weight > 33000:
        print(total_weight)
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
        if i.Priority == 0:
            load_task.priority = "客户催货"
        elif i.Priority == 1:
            load_task.priority = "超期库存"
        else:
            load_task.priority = ""
        load_task_list.append(load_task)
    return load_task_list


if __name__ == '__main__':
    result = dispatch()
    generate_excel_service.generate_excel(result)
