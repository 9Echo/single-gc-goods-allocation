# -*- coding: utf-8 -*-
# @Time    : 2020/03/12
# @Author  : shaoluyu
from app.main.steel_factory.entity.base_entity import BaseEntity


class Vehicle(BaseEntity):
    """
    车辆类
    """
    def __init__(self, vehicle=None):
        self.car_mark = None  # 车牌号
        self.commodity = None  # 运输品名
        self.weight = None  # 载重（t）
        self.city = None  # 运输城市
        self.end_point = None  # 运输区县
        self.mark = None  # 是否运输外库
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        if vehicle:
            self.set_attr(vehicle)
