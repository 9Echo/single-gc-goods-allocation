# -*- coding: utf-8 -*-
# @Time    : 2019/11/13
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class OrderItem(BaseEntity):
    """管厂订单子项"""

    def __init__(self, item):
        # 主键id
        self.rid = None
        # 主订单id
        self.order_id = None
        # 产品类型
        self.product_type = None
        # 产品规格
        self.spec = None
        # 数量(件数)
        self.quantity = None
        # 散根数
        self.free_pcs = None
        self.dest = None
        # 创建时间
        self.create_time = None
        # 更新时间
        self.update_time = None

        for attr in self.__dict__.keys():
            setattr(self, attr, item.setdefault(attr, None))
