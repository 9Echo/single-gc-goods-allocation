# -*- coding: utf-8 -*-
# Description: 钢铁配货服务
# Created: shaoluyu 2020/03/12
import copy
from typing import List
from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.rule.dispatch_filter import dispatch_filter, create_load_task
from app.main.steel_factory.service import stock_service
from app.util.enum_util import LoadTaskType
from datetime import datetime
from app.main.steel_factory.dao.load_task_dao import load_task_dao
from app.main.steel_factory.dao.load_task_item_dao import load_task_item_dao


def dispatch(id_list: List) -> List[LoadTask]:
    """
    车辆配货
    :param :
            id:
    :return:
    """
    load_task_list = list()
    # 库存信息获取
    stock_list, xg_dict = stock_service.deal_stock()
    surplus_stock_dict = dispatch_filter(load_task_list, stock_list, xg_dict)
    # 分不到标载车次的部分，甩掉，生成一个伪车次加明细
    if surplus_stock_dict:
        load_task_list.append(
            create_load_task(list(surplus_stock_dict.values()), datetime.now().strftime("%Y%m%d%H%M0000") + '0000',
                             LoadTaskType.TYPE_5.value))
    # 合并
    merge_result(load_task_list)
    load_task_list.sort(key=lambda x: (x.priority_grade, x.latest_order_time), reverse=False)
    # 写库
    save_load_task(load_task_list, id_list)
    return load_task_list


def merge_result(load_task_list: list):
    """合并结果中load_task_id相同的信息

    Args:
        load_task_list: load_task的列表
    Returns:

    Raise:

    """

    for load_task in load_task_list:
        result_dic = {}
        for item in load_task.items:
            # 按（车次ID，车次父ID）整理车次
            result_dic.setdefault(item.parent_load_task_id, []).append(item)
        # 暂时清空items
        load_task.items = []
        for res_list in result_dic.values():
            sum_list = [(i.weight, i.count) for i in res_list]
            sum_weight = sum(i[0] for i in sum_list)
            sum_count = sum(i[1] for i in sum_list)
            res_list[0].weight = sum_weight
            res_list[0].count = sum_count
            load_task.items.append(res_list[0])
        del result_dic


def save_load_task(load_task_list: List[LoadTask], id_list):
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
        task_tup = (id_list[0],
                    task.load_task_id,
                    task.load_task_type,
                    task.total_weight,
                    task.city,
                    task.end_point,
                    task.price_per_ton,
                    task.total_price,
                    task.remark,
                    task.priority_grade,
                    id_list[1],
                    create_date
                    )
        load_task_values.append(task_tup)
        for item in task.items:
            item_tup = (id_list[0],
                        task.load_task_id,
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
                        id_list[1],
                        create_date)
            load_task_item_values.append(item_tup)
    load_task_dao.insert_load_task(load_task_values)
    load_task_item_dao.insert_load_task_item(load_task_item_values)


if __name__ == '__main__':
    # print(datetime.now()[0:19])
    result = dispatch(["C000000882", "ct"])
    print("success")
    # generate_excel_service.generate_excel(result)
