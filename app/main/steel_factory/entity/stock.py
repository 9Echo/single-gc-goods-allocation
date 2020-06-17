# -*- coding: utf-8 -*-
# @Time    : 2020/03/31
# @Author  : shaoluyu
from app.util.base.base_entity import BaseEntity


class Stock(BaseEntity):
    """
    钢厂库存类
    """

    def __init__(self, stock=None):
        self.stock_id = None  # Id
        self.notice_num = None  # 发货通知单
        self.oritem_num = None  # 订单号
        self.priority = None  # 优先发运 1.客户催货 2.超期清理 3.其余
        self.consumer = None  # 收货用户
        self.commodity_name = None  # 品名名称
        self.big_commodity_name = None  # 品名
        self.mark = None  # 牌号
        self.specs = None  # 规格
        self.deliware_house = None  # 出库仓库
        self.province = None  # 省份
        self.city = None  # 城市
        self.dlv_spot_name_end = None  # 终点
        self.logistics_company_type = None  # 物流公司类型
        self.pack = None  # 包装形式
        self.detail_address = None  # 卸货地址
        self.latest_order_time = None  # 最新挂单时间
        self.devperiod = None  # 合同约定交货日期
        self.actual_weight: int = 0  # 实际可发重量
        self.actual_number: int = 0  # 实际可发件数
        self.piece_weight: int = 0  # 件重
        self.deliware = None  # 入库仓库
        self.longitude = None  # 经度
        self.latitude = None  # 纬度
        self.standard_address = None  # 合并卸货地址
        self.parent_stock_id = None  # 父Id
        self.actual_end_point = None  # 实际区县
        self.sort = None  # 排序用字段
        self.waint_fordel_number = None  # 待发件数
        self.waint_fordel_weight = None  # 待发重量
        self.notice_stockinfo_id = None
        self.can_send_number = None  # 可发件数
        if stock:
            self.set_attr(stock)
