# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:32
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
from app.main.entity.base_entity import BaseEntity
from app.main.entity.order_item import OrderItem
from app.utils.uuid_util import UuidUtil


class Order(BaseEntity):
    """管厂订单"""

    def __init__(self, order={}):
        if order:
            # 主键id
            self.rid = ""
            # 订单id
            self.order_id = UuidUtil.create_id('od')
            # 子项
            self.order_item = []
            for i in order['item']:
                i['order_id'] = self.order_id
                self.order_item.append(OrderItem(i))
            # 目的地
            # self.dest = order['dest']
            # 客户id
            self.customer_id = order['customer_id']
            # 业务员id
            self.salesman_id = order['salesman_id']
            self.create_time = ""                # 创建时间
            self.update_time = ""                # 更新时间
        else:
            # 主键id
            self.rid = ""
            # 订单id
            self.order_id = ""
            # 子项
            self.order_item = []
            # 目的地
            # self.dest = ""
            # 客户id
            self.customer_id = ""
            # 业务员id
            self.salesman_id = ""
            self.create_time = ""  # 创建时间
            self.update_time = ""  # 更新时间


