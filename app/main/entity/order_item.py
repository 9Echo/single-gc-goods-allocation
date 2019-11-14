# -*- coding: utf-8 -*-
# @Time    : 2019/11/13
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class OrderItem(BaseEntity):
    """管厂订单子项"""

    def __init__(self, item, order_id):
        # 主键id
        self.rid = ""
        # 主订单id
        self.order_id = order_id
        # 产品类型
        self.product_type = item['product_type']
        # 产品规格
        self.spec = item['spec']
        # 数量(件数)
        self.quantity = item['quantity'] if item['quantity'] is not None else 0
        # 散根数
        self.number = item['number'] if item['number'] is not None else 0
        # 创建时间
        self.create_time = ""
        # 更新时间
        self.update_time = ""

