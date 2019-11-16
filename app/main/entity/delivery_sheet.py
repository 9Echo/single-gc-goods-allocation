# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:23
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity
from app.main.entity.delivery_item import DeliveryItem
from app.utils.uuid_util import UuidUtil


class DeliverySheet(BaseEntity):
    """发货通知单"""

    def __init__(self, delivery_sheet=0):
        if isinstance(delivery_sheet, dict):
            self.rid = ""                       # 主键id
            self.delivery_no = UuidUtil.create_id('de')             # 发货通知单号
            self.batch_no = delivery_sheet['batch_no']                 # 批次号
            self.data_address = delivery_sheet["data_address"]               # 数据来源
            self.items = [DeliveryItem(i) for i in delivery_sheet["items"]]                      # 发货通知单子单
            self.total_quantity = delivery_sheet["total_quantity"]             # 总件数
            self.free_pcs = delivery_sheet["free_pcs"]                   # 散根数
            self.total_pcs = delivery_sheet["total_pcs"]                # 总根数
            self.weight = delivery_sheet["weight"]                      # 理重
            self.create_time = delivery_sheet["create_time"]                # 创建时间
            self.update_time = delivery_sheet["update"]                # 更新时间
        elif delivery_sheet == 0:
            self.rid = ""  # 主键id
            self.delivery_no = ""  # 发货通知单号
            self.batch_no = ""  # 批次号
            self.data_address = ""  # 数据来源
            self.items = []  # 发货通知单子单
            self.total_quantity = 0  # 总件数
            self.free_pcs = 0  # 散根数
            self.total_pcs = 0  # 总根数
            self.weight = ""   # 理重
            self.create_time = ""  # 创建时间
            self.update_time = ""  # 更新时间
