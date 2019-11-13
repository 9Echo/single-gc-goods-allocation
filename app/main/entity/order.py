# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:32
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
from app.main.entity.base_entity import BaseEntity


class Order(BaseEntity):
    """管厂订单"""

    def __int__(self, order):
        self.rid = ""                      # 主键id
        self.order_id = ""                   # 订单id
        self.order_item = []                 # 子项
        self.dest = ""                       # 目的地
        self.customer_id = ""                # 客户id
        self.salesman_id = ""                # 业务员id
        self.create_time = ""                # 创建时间
        self.update_time = ""                # 更新时间

