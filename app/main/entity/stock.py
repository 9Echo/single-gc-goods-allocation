# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:57
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class Stock(BaseEntity):
    """"库存"""

    def __init__(self, stock=None):
        self.rid = None  # 表主键id
        self.product_id = None  # 产品id(物资代码，唯一值)
        self.product_type = None  # 产品名
        self.spec = None  # 规格
        self.quantity = None  # 数量
        self.free_pcs = None  # 散根数
        self.warehouse = None  # 仓库
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        if stock:
            self.set_attr(stock)
