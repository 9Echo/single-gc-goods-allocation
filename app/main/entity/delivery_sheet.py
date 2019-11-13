# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:23
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class DeliverySheet(BaseEntity):
    """发货通知单"""

    def __int__(self, delivery):
        self.rid = ""                        # 主键id
        self.delivery_no = ""                # 发货通知单号
        self.batch_no = ""                   # 批次号
        self.data_address = ""               # 数据来源
        self.items = []                      # 发货通知单子单
        self.total_quantity = ""             # 总件数
        self.free_pcs = ""                   # 散根数
        self.total_pcs = ""                  # 总根数
        self.create_time = ""                # 创建时间
        self.update_time = ""                # 更新时间
