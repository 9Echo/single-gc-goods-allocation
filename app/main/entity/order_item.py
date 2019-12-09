# -*- coding: utf-8 -*-
# @Time    : 2019/11/13
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class OrderItem(BaseEntity):
    """管厂订单子项"""

    def __init__(self, item=None):
        self.rid = None  # 主键id
        self.order_no = None  # 主订单id
        self.product_type = None  # 产品类型
        self.spec = None  # 产品规格
        self.quantity = None  # 数量(件数)
        self.free_pcs = None  # 散根数
        self.dest = None  # 目的地
        self.weight = 0 # 重量（使用公式计算)
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        if item:
            self.set_attr(item)
