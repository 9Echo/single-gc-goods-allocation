# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:25
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity
from app.utils.uuid_util import UuidUtil


class DeliveryItem(BaseEntity):
    """发货通知单子项"""

    def __init__(self, delivery_item):
        self.rid = None  # 主键id
        self.delivery_no = None  # 发货通知单主单号
        self.delivery_item_no = UuidUtil.create_id('delivery_item')  # 子单号
        self.customer_id = None  # 客户id
        self.salesman_id = None  # 业务员id
        self.dest = None  # 目的地
        self.product_type = None  # 产品类型
        self.spec = None  # 产品规格
        self.weight = None  # 产品重量
        self.warehouse = None  # 仓库信息
        self.loc_id = None  # 库位信息
        self.quantity = None  # 总数
        self.free_pcs = None  # 散根数
        self.total_pcs = None  # 总根数
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间

        for attr in self.__dict__.keys():
            setattr(self, attr, delivery_item.setdefault(attr, None))
