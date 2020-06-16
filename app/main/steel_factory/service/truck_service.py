# -*- coding: utf-8 -*-
# Description: 车辆实例化服务
# Created: shaoluyu 2020/06/16
from typing import List

from app.main.steel_factory.entity.truck import Truck


def generate_truck(json_data):
    """
    车辆信息实例化
    :param json_data:
    :return:
    """
    truck_list: List[Truck] = [Truck(i) for i in json_data]
    return truck_list
