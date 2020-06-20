# -*- coding: utf-8 -*-
# Description: 单车配载服务
# Created: shaoluyu 2020/06/16
from app.main.steel_factory.rule import single_dispatch_filter


def dispatch(truck):
    """
    进行单车分货
    """
    load_task = single_dispatch_filter.dispatch(truck)
    if load_task:
        load_task.schedule_no = truck.schedule_no
        load_task.car_mark = truck.car_mark
    # 生成的车次信息保存入库

    return load_task
