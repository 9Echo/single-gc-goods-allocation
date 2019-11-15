# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:25
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class DeliveryItem(BaseEntity):
    """发货通知单子项"""

    def __init__(self, delivery_item=0):

        if isinstance(delivery_item, dict):
            self.rid = ""                  # 主键id
            self.delivery_no = delivery_item["delivery_no"]            # 发货通知单主单号
            self.delivery_item_no = delivery_item["delivery_item_no"]       # 子单号
            self.customer_id = delivery_item["customer_id"]            # 客户id
            self.salesman_id = delivery_item["salesman_id"]            # 业务员id
            self.dest = delivery_item["dest"]                   # 目的地
            self.product_type = delivery_item["product_type"]           # 产品类型
            self.spec = delivery_item["spec"]                   # 产品规格
            self.weight = delivery_item["weight"]                 # 产品重量
            self.warehouse = delivery_item["warehouse"]              # 仓库信息
            self.loc_id = delivery_item["loc_id"]                  # 库位信息
            self.quantity = delivery_item["quantity"]               # 总数
            self.free_pcs = delivery_item["free_pcs"]               # 散根数
            self.total_pcs = delivery_item["total_pcs"]              # 总根数
            self.create_time = delivery_item["create_time"]            # 创建时间
            self.update_time = delivery_item["update_time"]            # 更新时间

        elif delivery_item == 0:
            self.rid = ""  # 主键id
            self.delivery_no = ""  # 发货通知单主单号
            self.delivery_item_no = ""  # 子单号
            self.customer_id = ""  # 客户id
            self.salesman_id = ""  # 业务员id
            self.dest = ""  # 目的地
            self.product_type = ""  # 产品类型
            self.spec = ""  # 产品规格
            self.weight = ""  # 产品重量
            self.warehouse = ""  # 仓库信息
            self.loc_id = ""  # 库位信息
            self.quantity = 0  # 总数
            self.free_pcs = 0  # 散根数
            self.total_pcs = 0  # 总根数
            self.create_time = ""  # 创建时间
            self.update_time = ""  # 更新时间


