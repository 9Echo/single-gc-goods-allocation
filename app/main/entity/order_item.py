# -*- coding: utf-8 -*-
# @Time    : 2019/11/13
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class OrderItem(BaseEntity):
    """管厂订单子项"""

    def __int__(self, item, order_id):
        self.rid = ""                      # 主键id
        self.order_id = order_id                  # 主订单id
        self.product_type = item['product_type']               # 产品类型
        self.spec = item['product_type']                       # 产品规格
        self.quantity = item['quantity']                   # 数量
        self.create_time = ""                # 创建时间
        self.update_time = ""                # 更新时间

