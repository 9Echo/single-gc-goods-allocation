# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:25
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class DeliveryItem(BaseEntity):
    """发货通知单子项"""

    def __init__(self, delivery_item=None):
        self.rid = None  # 主键id
        self.delivery_no = None  # 发货通知单主单号
        self.delivery_item_no = None  # 子单号
        self.order_no = None # 订单号
        self.product_type = None  # 产品类型
        self.item_id = None
        self.spec = None  # 产品规格
        self.weight = None  # 产品重量
        self.weightone = None  # 根重
        self.warehouse = None  # 仓库信息
        self.loc_id = None  # 库位信息
        self.quantity = None  # 总数
        self.free_pcs = None  # 散根数
        self.total_pcs = None  # 总根数
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        if delivery_item:
            self.set_attr(delivery_item)
