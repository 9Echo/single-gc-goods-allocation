# -*- coding: utf-8 -*-
# Description: 车辆实例化服务
# Created: shaoluyu 2020/06/16
from typing import List

import pandas as pd

from app.main.steel_factory.entity.truck import Truck
from app.util.get_static_path import get_path


def generate_truck(json_data):
    """
    车辆信息实例化
    :param json_data:
    :return:
    """
    truck_list: List[Truck] = [Truck(i) for i in json_data]
    return truck_list


def get_truck(file_name):
    """
    获取库存
    :param vehicle:
    :return: 库存
    """
    """
    步骤：
    1 读取Excel，省内1  0点库存明细和省内2、3及连云港库存两个sheet页
    2 数据合并
    """
    data_path = get_path(file_name)
    df_truck = pd.read_excel(data_path)

    return df_truck
