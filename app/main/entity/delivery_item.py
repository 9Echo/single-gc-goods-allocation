# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:25
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class DeliveryItem(BaseEntity):
    """发货通知单子项"""

    def __init__(self):
        self.rid = ""                    # 主键id
        self.delivery_no = ""            # 发货通知单主单号
        self.delivery_item_no = ""       # 子单号
        self.customer_id = ""            # 客户id
        self.salesman_id = ""            # 业务员id
        self.dest = ""                   # 目的地
        self.product_type = ""           # 产品类型
        self.spec = ""                   # 产品规格
        self.weight = ""                 # 产品重量
        self.warehouse = ""              # 仓库信息
        self.quantity = ""               # 总数
        self.free_pcs = ""               # 散根数
        self.total_pcs = ""              # 总根数
        self.create_time = ""            # 创建时间
        self.update_time = ""            # 更新时间
