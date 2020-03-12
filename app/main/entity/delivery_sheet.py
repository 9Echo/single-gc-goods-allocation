# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:23
# @Author  : Zihao.Liu

from app.main.entity.base_entity import BaseEntity


class DeliverySheet(BaseEntity):
    """提货单类"""

    def __init__(self, delivery_sheet=None):
        self.rowid = None  # 主键id
        self.load_task_id = None  # 所属车次号
        self.car_mark = None  # 车牌号
        self.city = None  # 城市
        self.delivery_no = None  # 发货通知单号
        self.company_id = None  # 公司id
        self.batch_no = None  # 批次号
        self.status = None  # 状态 00：预留 10：已生成，20：已打印
        self.customer_id = None  # 客户id
        self.salesman_id = None  # 业务员id
        self.total_pcs = None  # 总根数
        self.weight = None  # 重量
        self.type = None  # 类型
        self.volume = None  # 所占体积
        self.items = []  # 发货通知单子单
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        if delivery_sheet:
            self.set_attr(delivery_sheet)
