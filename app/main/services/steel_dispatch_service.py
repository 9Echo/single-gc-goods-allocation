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
    load_task_list = list()
    # 库存信息获取
    stock_list: List[Stock] = stock_service.deal_stock()
    # 标载车次列表
    standard_stock_list = list(
        filter(lambda x: x.CANSENDWEIGH >= ModelConfig.RG_MIN_WEIGHT, stock_list))
    # 普通车次列表
    general_stock_list = list(
        filter(lambda x: x.CANSENDWEIGH < ModelConfig.RG_MIN_WEIGHT, stock_list))
    # 标载车次拼凑一装一卸小件货物
    for standard_stock in standard_stock_list:
        # 可拼车列表
        compose_list = list()
        # 车次剩余载重
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - standard_stock.CANSENDWEIGHT
        # 筛选符合拼车条件的库存列表
        temp_list = list(filter(lambda x: x.DELIWAREHOUSE == standard_stock.DELIWAREHOUSE
                                          and x.DETAILADDRESS == standard_stock.DETAILADDRESS
                                          and x.CANSENDWEIGH <= surplus_weight
                                          and x.COMMODITYNAME in ModelConfig.RG_COMMODITY_GROUP.get(
            standard_stock.COMMODITYNAME), general_stock_list))
        # 如果有，按照surplus_weight为背包上限进行匹配
        if temp_list:
            compose_list = goods_filter(standard_stock, temp_list, surplus_weight)
        # 生成车次数据
        load_task_list.extend(create_load_task(compose_list + [standard_stock], load_task_id))


def goods_filter(stock: Stock, general_stock_list: List[Stock], surplus_weight: int) -> List[Stock]:
    """
    背包过滤方法
    :param surplus_weight:
    :param general_stock_list:
    :param stock:
    :return:
    """
    compose_list = list()
    weight_list = ([item.CANSENDWEIGHT for item in general_stock_list])
    value_list = copy.deepcopy(weight_list)
    result_index_list = pulp_solve.pulp_pack(weight_list, None, value_list, surplus_weight)
    for index in sorted(result_index_list, reverse=True):
        compose_list.append(general_stock_list[index])
        general_stock_list.pop(index)
    # 数据返回
    return compose_list


def create_load_task(stock_list: List[Stock], load_task_id) -> List[LoadTask]:
    """
    车次创建方法
    :param stock_list:
    :param load_task_id:
    :return:
    """
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
