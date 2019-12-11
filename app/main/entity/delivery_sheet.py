# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:23
# @Author  : Zihao.Liu

from app.main.entity.base_entity import BaseEntity


class DeliverySheet(BaseEntity):
    """发货通知单"""

    def __init__(self, delivery_sheet=None):
        self.rid = None  # 主键id
        self.load_task_id = None  # 所属车次号
        self.delivery_no = None  # 发货通知单号
        self.batch_no = None  # 批次号
        self.status = None  # 状态 00：预留 10：已生成，20：已打印
        self.customer_id = None  # 客户id
        self.salesman_id = None # 业务员id
        self.weight = None # 重量
        self.items = []  # 发货通知单子单
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        if delivery_sheet:
            self.set_attr(delivery_sheet)
