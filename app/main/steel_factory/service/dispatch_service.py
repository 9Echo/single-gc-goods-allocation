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
from datetime import datetime
from app.main.steel_factory.dao.load_task_dao import LoadTaskDao
from app.main.steel_factory.dao.load_task_item_dao import LoadTaskItemDao


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
        load_task_list.append(create_load_task(list(surplus_stock_dict.values()), -1, LoadTaskType.TYPE_5.value))
    return merge_result(load_task_list)


def merge_result(load_task_list: list):
    """合并结果中load_task_id相同的信息

    Args:
        load_task_list: load_task的列表
    Returns:

    Raise:

    """
    result_dic = {}
    last_result = []
    load_task_dic = {}
    latest_order_time = set()
    priority_set = set()
    for load_task in load_task_list:
        load_task_last = copy.deepcopy(load_task)
        load_task_last.items = []
        load_task_dic.setdefault(load_task.load_task_id, load_task)
        for item in load_task.items:
            # 整理每个车次的所有最新挂单时间
            latest_order_time.add(item.latest_order_time)
            # 整理每个车次的所有优先级
            priority_set.add(4 if not item.priority else ModelConfig.RG_PRIORITY[item.priority])
            # 按（车次ID，车次父ID）整理车次
            result_dic.setdefault(item.parent_load_task_id, []).append(item)
        for res in result_dic:
            res_list = result_dic[res]
            if len(res_list) > 1:
                sum_list = [(i.weight, i.count) for i in res_list]
                sum_weight = sum(i[0] for i in sum_list)
                sum_count = sum(i[1] for i in sum_list)
                res_list[0].weight = sum_weight
                res_list[0].count = sum_count
        load_task_last.latest_order_time = min(latest_order_time)
        load_task_last.priority_grade = ModelConfig.RG_PRIORITY_GRADE[min(priority_set)]
        load_task_last.items.append(res_list[0])
        last_result.append(load_task_last)
    last_result.sort(key=lambda x: (x.priority_grade, x.latest_order_time), reverse=False)
    return last_result


def save_load_task(load_task_list: List[LoadTask]):
    """将load_task对象的信息写入数据库
    分load_task和load_task_item
    Args:

    Returns:

    Raise:

    """
    load_task_values = []
    load_task_item_values = []
    create_date = datetime.now()
    for task in load_task_list:
        task_tup = (task.company_id,
                    task.load_task_id,
                    task.load_task_type,
                    task.total_weight,
                    task.city,
                    task.end_point,
                    task.price_per_ton,
                    task.total_price,
                    task.remark,
                    task.priority_grade,
                    task.create_id,
                    create_date
                    )
        load_task_values.append(task_tup)
        for item in task.items:
            item_tup = (task.company_id,
                        item.load_task_id,
                        item.priority,
                        item.weight,
                        item.count,
                        item.city,
                        item.end_point,
                        item.big_commodity,
                        item.commodity,
                        item.notice_num,
                        item.oritem_num,
                        item.consumer,
                        item.standard,
                        item.sgsign,
                        item.outstock_code,
                        item.instock_code,
                        item.receive_address,
                        item.latest_order_time,
                        task.create_id,
                        create_date)
            load_task_item_values.append(item_tup)
    LoadTaskDao.insert_load_task(load_task_values)
    LoadTaskItemDao.insert_load_task_item(load_task_item_values)


if __name__ == '__main__':
    print(datetime.now()[0:19])
    # result = dispatch()
    # print("success")
    # generate_excel_service.generate_excel(result)
