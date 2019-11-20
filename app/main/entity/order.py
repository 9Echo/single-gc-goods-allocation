# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:32
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13

from app.main.entity.base_entity import BaseEntity


class Order(BaseEntity):
    """管厂订单"""

    def __init__(self, order=None):
        self.rid = None  # 主键id
        self.order_id = None  # 订单id
        self.order_items = []  # 订单子项
        # self.dest = None # 目的地
        self.customer_id = None  # 客户id
        self.salesman_id = None  # 业务员id
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        if order:
            self.set_attr(order)



