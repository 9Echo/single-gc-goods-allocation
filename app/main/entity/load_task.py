# -*- coding: utf-8 -*-
# @Time    :
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class LoadTask(BaseEntity):
    """车次类"""
    type_1 = "一装一卸"
    type_2 = "一装两卸"
    type_3 = "两装一卸"

    def __init__(self):
        self.load_task_id = None  # 所属车次号
        # 优先级
        self.priority = 0
        # 装卸类型
        self.load_task_type = None
        # 总重量
        self.total_weight = 0
        # 发货通知单重量
        self.weight = 0
        # 发货通知单件数
        self.count = 0
        # 城市
        self.city = None
        # 区县
        self.end_point = None
        # 品种
        self.commodity = None
        # 发货通知单号
        self.notice_num = None
        # 订单项次号
        self.oritem_num = None
        # 规格
        self.standard = None
        # 材质
        self.sgsign = None
        # 出库仓库
        self.outstock_code = None
        # 入库仓库
        self.instock_code = None
