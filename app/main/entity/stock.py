# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 15:57
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class Stock(BaseEntity):
    """库存"""

    def __int__(self):
        rid = ""                        # 表主键id
        item_id = ""                    # 产品id
        item_name = ""                  # 产品名
        spec = ""                       # 规格
        quantity = ""                   # 数量
        warehouse = ""                  # 仓库
        create_time = ""                # 创建时间
        update_time = ""                # 更新时间
