# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:57
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class Stock(BaseEntity):
    """库存"""

    def __init__(self, stock):
        self.rid = ""                        # 表主键id
        self.product_id = ""                 # 产品id
        self.product_type = ""               # 产品名
        self.spec = ""                       # 规格
        self.quantity = ""                   # 数量
        self.free_pcs = ""                   # 散根数
        self.warehouse = ""                  # 仓库
        self.create_time = ""                # 创建时间
        self.update_time = ""                # 更新时间

        for attr in self.__dict__.keys():
            setattr(self, attr, stock.setdefault(attr, None))

