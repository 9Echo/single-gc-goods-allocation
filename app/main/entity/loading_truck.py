# -*- coding: utf-8 -*-
# @Time    : 2020/03/19 15:32
# @Author  : zhouwentao

from app.main.entity.base_entity import BaseEntity


class LoadingTruck(BaseEntity):
    """装配载车辆"""

    def __init__(self, loading_truck=None):
        self.rowid = None  # 主键id
        self.load_task_id = None  # 所属车次号
        self.total_height_in=None #内侧总高度
        self.total_height_out=None #外侧总高度
        self.loading_floors = []  # 配载每层的具体货物
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        if loading_truck:
            self.set_attr(loading_truck)