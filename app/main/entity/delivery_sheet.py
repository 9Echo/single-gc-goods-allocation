# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:23
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class DeliverySheet(BaseEntity):
    """发货通知单"""

    def __int__(self):
        rid = ""                        # 主键id
        delivery_no = ""                # 发货通知单号
        batch_no = ""                   # 批次号
        data_address = ""               # 数据来源
        items = []                      # 发货通知单子单
        total_quantity = ""             # 总件数
        free_pcs = ""                   # 散根数
        total_pcs = ""                  # 总根数
        create_time = ""                # 创建时间
        update_time = ""                # 更新时间
