# -*- coding: utf-8 -*-
# Description: 钢铁配货服务
# Created: shaoluyu 2020/03/12
import copy
import math
from typing import List, Dict, Any, Tuple

from app.main.entity.load_task import LoadTask
from app.main.entity.stock import Stock
from app.main.services import stock_service
from app.task.pulp_task.analysis.rules import pulp_solve
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
    5 重复3和4，直到结束
    """

    load_task_id = 0
    # 根据车辆条件获取库存
    end_point_stock_list_dict: Dict[str, List[Stock]] = dict()
    result_list: List[LoadTask] = list()
    stock_list: List[Stock] = stock_service.deal_stock()
    for i in copy.copy(stock_list):
        if 31000 <= i.CANSENDWEIGHT <= 33000:
            pass
    for i in stock_list:
        end_point_stock_list_dict.setdefault(i.end_point, []).append(i)
    # 过滤库存，调用算法进行配货
    for k, v in end_point_stock_list_dict.items():
        load_task_list: List[LoadTask] = goods_filter(k, v)
        result_list.extend(load_task_list)
    return result_list


def goods_filter(end_point: str, stock_list: List) -> List[LoadTask]:
    """
    :param end_point:
    :param stock_list:
    :return:
    """
    surplus_list: List[Stock] = list()
    load_task_result: List[LoadTask] = list()
    name_stock_list_dict: Dict[str, List[Stock]] = dict()
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


def limit_stock(stock_list: List[Stock]) -> List[LoadTask]:
    """

    :param stock_list:
    :return:
    """
    load_task_list: List[LoadTask] = list()
    while stock_list:
        stock_list.sort(key=lambda x: x.end_point)
        total_weight: float = 0
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


def split_item(item: Stock, delta_weight: float) -> Tuple[Stock, Stock]:
    """

    :param item:
    :param delta_weight:
    :return:
    """
    new_cunt: int = math.ceil(delta_weight / item.CANSENDWEIGHT * item.CANSENDNUMBER)
    new_weight: float = new_cunt * (item.CANSENDWEIGHT / item.CANSENDNUMBER)

    new_item = copy.deepcopy(item)
    new_item.CANSENDWEIGHT = new_weight
    new_item.CANSENDNUMBER = new_cunt
    item.CANSENDWEIGHT = item.CANSENDWEIGHT - new_weight
    item.CANSENDNUMBER = item.CANSENDNUMBER - new_cunt
    return item, new_item


def create_load_task(stock_list: List[Stock], load_task_id) -> List[LoadTask]:
    total_weight = sum(i.CANSENDWEIGHT for i in stock_list)
    load_task_id += 1
    load_task_list = list()
    for i in stock_list:
        load_task = LoadTask()
        load_task.load_task_id = load_task_id
        load_task.total_weight = total_weight
        load_task.weight = i.CANSENDWEIGHT
        load_task.count = i.CANSENDNUMBER
        load_task.city = i.CITY
        load_task.end_point = i.REGIONS
        load_task.commodity = i.COMMODITYNAME
        load_task.notice_num = i.NOTICENUM
        load_task.oritem_num = i.ORITEMNUM
        load_task.standard = i.STANDARD
        load_task.sgsign = i.MATERIAL
        load_task.outstock_code = i.DELIWAREHOUSE
        load_task.instock_code = i.DELIWARE
        load_task_list.append(load_task)
    return load_task_list


if __name__ == '__main__':
    result = dispatch()
    stad_list = list(filter(lambda x: x.weight > 30000, result))
    print(len(stad_list))
