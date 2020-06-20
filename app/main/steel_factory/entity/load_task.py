# -*- coding: utf-8 -*-
# @Time    :
# @Author  : shaoluyu
from app.util.base.base_entity import BaseEntity


class LoadTask(BaseEntity):
    """车次类"""

    def __init__(self):
        # 报道号
        self.schedule_no = None
        # 车牌号
        self.car_mark = None
        # 所属车次号
        self.load_task_id = None
        # 装卸类型
        self.load_task_type = None
        # 总重量
        self.total_weight = 0
        # 城市
        self.city = None
        # 区县
        self.end_point = None
        # 车次吨单价
        self.price_per_ton = 0
        # 车次总价
        self.total_price = 0
        # 注释
        self.remark = None
        # 优先级对应的ABCD等级
        self.priority_grade = None
        # 子项
        self.items = []
        # 最新挂单时间
        self.latest_order_time = None
