# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:32
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class Order(BaseEntity):
    """管厂订单"""

    def __int__(self):
        rid = ""                        # 主键id
        order_id = ""                   # 订单id
        product_type = ""               # 产品类型
        spec = ""                       # 产品规格
        quantity = ""                   # 数量
        dest = ""                       # 目的地
        customer_id = ""                # 客户id
        salesman_id = ""                # 业务员id
        create_time = ""                # 创建时间
        update_time = ""                # 更新时间
