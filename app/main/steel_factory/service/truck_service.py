# -*- coding: utf-8 -*-
# Description: 车辆实例化服务
# Created: shaoluyu 2020/06/16

from app.main.steel_factory.entity.truck import Truck
from app.util.code import ResponseCode
from app.util.my_exception import MyException
from model_config import ModelConfig


def generate_truck(json_data):
    """
    车辆信息实例化
    :param json_data:
    :return:
    """
    truck = Truck()
    truck.schedule_no = json_data['schedule_no']
    truck.car_mark = json_data['car_mark']
    truck.driver_id = json_data['driver_id']
    truck.trans_group_name = json_data['trans_group_name']
    truck.province = json_data['province']
    truck.city = json_data['city']
    truck.dlv_spot_name_end = json_data['dlv_spot_name_end']
    truck.big_commodity_name = json_data['big_commodity_name']
    truck.load_weight = float(json_data['load_weight'])
    truck.remark = json_data['remark']
    truck.actual_end_point = ModelConfig.RG_LY_GROUP.get(truck.dlv_spot_name_end, [truck.dlv_spot_name_end])
    # 必填字段非空检查
    if not truck.dlv_spot_name_end or not truck.big_commodity_name or not truck.load_weight:
        raise MyException('必填参数值缺失', ResponseCode.Error)
    return truck
