# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:25
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class DeliveryItem(BaseEntity):
    """发货通知单子项"""

    def __int__(self):
        rid = ""                    # 主键id
        main_id = ""                # 发货通知单主表id
        item_no = ""                # 子单号
        customer_id = ""            # 客户id
        salesman_id = ""            # 业务员id
        dest = ""                   # 目的地
        product_type = ""           # 产品类型
        spec = ""                   # 产品规格
        weight = ""                 # 产品重量
        warehouse = ""              # 仓库信息
        quantity = ""               # 总数
        free_pcs = ""               # 散根数
        total_pcs = ""              # 总根数
        create_time = ""            # 创建时间
        update_time = ""            # 更新时间
