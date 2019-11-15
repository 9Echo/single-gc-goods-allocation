# -*- coding: utf-8 -*-
# @Time    : 2019/11/13
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class OrderItem(BaseEntity):
    """管厂订单子项"""

    def __init__(self, item=0, order_id=0):

        if isinstance(item, dict):
            # 主键id
            self.rid = ""
            # 主订单id
            self.order_id = order_id
            # 产品类型
            self.product_type = item['product_type']
            # 产品规格
            self.spec = item['spec']
            # 数量(件数)
            self.quantity = int(item['quantity']) if item['quantity'] is not None else 0
            # 散根数
            self.free_pcs = int(item['free_pcs']) if item['free_pcs'] is not None else 0
            # 创建时间
            self.create_time = ""
            # 更新时间
            self.update_time = ""
        elif item == 0 and order_id == 0:
            # 主键id
            self.rid = ""
            # 主订单id
            self.order_id = ""
            # 产品类型
            self.product_type = ""
            # 产品规格
            self.spec = ""
            # 数量(件数)
            self.quantity = ""
            # 散根数
            self.free_pcs = ""
            # 创建时间
            self.create_time = ""
            # 更新时间
            self.update_time = ""

