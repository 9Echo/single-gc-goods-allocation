# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:23
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class DeliverySheet(BaseEntity):
    """发货通知单"""

    def __init__(self, delivery_sheet=None):
        self.rid = None  # 主键id
        self.delivery_no = None  # 发货通知单号
        self.batch_no = None  # 批次号
        self.status = None # 状态 0：待确认 1：已确认
        self.data_address = None  # 数据来源
        self.items = []  # 发货通知单子单
        self.total_quantity = None  # 总件数
        self.free_pcs = None  # 散根数
        self.total_pcs = None  # 总根数
        self.weight = None  # 理重
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        if delivery_sheet:
            self.set_attr(delivery_sheet)

