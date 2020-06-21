# -*- coding: utf-8 -*-
# Description: 单车配载服务
# Created: shaoluyu 2020/06/16
from datetime import datetime
from app.main.steel_factory.dao.load_task_dao import load_task_dao
from app.main.steel_factory.dao.load_task_item_dao import load_task_item_dao
from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.rule import single_dispatch_filter
from app.util.result import Result


def dispatch(truck):
    """
    进行单车分货
    """
    load_task = single_dispatch_filter.dispatch(truck)
    if load_task:
        load_task.schedule_no = truck.schedule_no
        load_task.car_mark = truck.car_mark
    # 生成的车次信息保存入库
    save_load_task(load_task)
    # 平台微服务所需格式转换
    load_task_dict = data_format(load_task)
    return Result.success(data=load_task_dict)


def data_format(load_task: LoadTask):
    """
    格式转换
    :param load_task:
    :return:
    """
    if load_task:
        dic = {
            "loadTaskId": load_task.load_task_id,  # 车次号
            "loadTaskType": load_task.load_task_type,  # 装卸类型
            "priorityGrade": load_task.priority_grade,  # 车次优先级
            "totalWeight": load_task.total_weight,  # 总重量
            "city": load_task.city,  # 城市
            "dlvSpotNameEnd": load_task.end_point,
            "earliestOrderTime": load_task.latest_order_time,
            "items": [{
                "loadTaskId": item.load_task_id,
                "priority": item.priority,
                "weight": item.weight,
                "count": item.count,
                "city": item.city,
                "dlvSpotNameEnd": item.end_point,
                "bigCommodity": item.big_commodity,
                "commodityName": item.commodity,
                "noticeNum": item.notice_num,
                "oritemNum": item.oritem_num,
                "consumer": item.consumer,
                "standard": item.standard,
                "material": item.sgsign,
                "deliware": item.instock_code,
                "deliwareHouse": item.outstock_code,
                "detailAddresss": item.receive_address,
                "latestOrderTime": item.latest_order_time
            } for item in load_task.items]
        }
        return dic
    else:
        return None


def save_load_task(load_task: LoadTask):
    load_task_values = []
    load_task_item_values = []
    create_date = datetime.now()
    load_task_tuple = (
        'C000000882',
        load_task.schedule_no,
        load_task.car_mark,
        load_task.load_task_id,
        load_task.load_task_type,
        load_task.total_weight,
        load_task.city,
        load_task.end_point,
        '',
        '',
        load_task.remark,
        load_task.priority_grade,
        '',
        create_date)
    load_task_values.append(load_task_tuple)
    for item in load_task.items:
        item_tuple = (
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
            create_date)
        load_task_item_values.append(item_tuple)
    load_task_dao.insert_load_task(load_task_values)
    load_task_item_dao.insert_load_task_item(load_task_item_values)
