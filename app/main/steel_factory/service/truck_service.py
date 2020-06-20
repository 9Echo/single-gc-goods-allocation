# -*- coding: utf-8 -*-
# Description: 车辆实例化服务
# Created: shaoluyu 2020/06/16

import pandas as pd
from app.main.steel_factory.entity.truck import Truck
from model_config import ModelConfig


def generate_truck(json_data):
    """
    车辆信息实例化
    :param json_data:
    :return:
    """
    truck = Truck(json_data)
    truck.actual_end_point = ModelConfig.RG_LY_GROUP.get(truck.dlv_spot_name_end, [truck.dlv_spot_name_end])
    return truck
