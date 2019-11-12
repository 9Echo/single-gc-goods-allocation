# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:57
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class Stock(BaseEntity):
    """库存"""

    def __int__(self):
        self.rid = ""                        # 表主键id
        self.item_id = ""                    # 产品id
        self.item_name = ""                  # 产品名
        self.spec = ""                       # 规格
        self.quantity = ""                   # 数量
        self.warehouse = ""                  # 仓库
        self.create_time = ""                # 创建时间
        self.update_time = ""                # 更新时间
