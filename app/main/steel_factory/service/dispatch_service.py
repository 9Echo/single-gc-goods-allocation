# -*- coding: utf-8 -*-
# Description: 钢铁配货服务
# Created: shaoluyu 2020/03/12
import copy
from typing import List, Dict
from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule.dispatch_filter import dispatch_filter, create_load_task, goods_filter
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
    surplus_stock_dict = dispatch_filter(load_task_list, stock_list)
    # 分不到标载车次的部分，甩掉，生成一个伪车次加明细
    if surplus_stock_dict:
        load_task_list.extend(create_load_task(list(surplus_stock_dict.values()), -1, LoadTaskType.TYPE_5.value))
    return merge_result(load_task_list)


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


if __name__ == '__main__':
    result = dispatch()
    generate_excel_service.generate_excel(result)
