# -*- coding: utf-8 -*-
# Description: 钢铁配货服务
# Created: shaoluyu 2020/03/12
import copy
from typing import List, Dict
from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule.dispatch_filter import dispatch_filter, create_load_task, merge_result, goods_filter
from app.main.steel_factory.service import stock_service
from app.main.steel_factory.service import generate_excel_service
from app.util.enum_util import LoadTaskType, DispatchType
from app.util.generate_id import TrainId
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
                                            and x.Standard_address == standard_stock.Standard_address
                                            and x.Actual_weight <= surplus_weight
                                            and x.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(
            standard_stock.Big_product_name), general_stock_list))
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
            general_stock_dict[i.Stock_id] = i
        first_surplus_stock_dict = dispatch_filter(general_stock_dict, load_task_list, DispatchType.FIRST,
                                                   ModelConfig.RG_MIN_WEIGHT)
        surplus_stock_dict = dispatch_filter(first_surplus_stock_dict, load_task_list, DispatchType.SECOND,
                                             ModelConfig.SECOND_RG_MIN_WEIGHT)
        # 分不到标载车次的部分，甩掉，生成一个伪车次加明细
        if surplus_stock_dict:
            load_task_list.extend(create_load_task(list(surplus_stock_dict.values()), -1, LoadTaskType.TYPE_5.value))
    return merge_result(load_task_list)


if __name__ == '__main__':
    result = dispatch()
    generate_excel_service.generate_excel(result)
