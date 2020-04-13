# -*- coding: utf-8 -*-
# @Time    : 2020/03/31
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class Stock(BaseEntity):
    """
    钢厂库存类
    """

    def __init__(self, stock=None):
        self.id = None  # 主键id
        self.NOTICENUM = None  # 所属车次号
        self.SALEDEPT = None  # 内层剩余宽度
        self.SALEMANAGER = None  # 外层剩余宽度
        self.PRODCOMPANY = None  # 所属层数
        self.PURCHUNIT = None  # 每层内侧高度
        self.ENDCUSTMER = None  # 每层外侧高度
        self.MOTHERNUM = None  # 内侧装配货物
        self.ORITEMNUM = None # 外侧装配货物
        self.DEVPERIOD = None  # 装配的货物
        self.DELIWAREHOUSE = None  # 创建时间
        self.TRANSWAY = None  # 更新时间
        self.COMMODITYNAME = None  # 主键id
        self.PACK = None  # 所属车次号
        self.QUALITY = None  # 内层剩余宽度
        self.MATERIAL = None  # 外层剩余宽度
        self.STANDARD = None  # 所属层数
        self.THICKNESS = None  # 每层内侧高度
        self.WIDTH = None  # 每层外侧高度
        self.LENGTH = None  # 内侧装配货物
        self.DELIWARE = None  # 外侧装配货物
        self.PORTNUM = None  # 装配的货物
        self.ADDRESS = None  # 创建时间
        self.DETAILADDRESS = None  # 更新时间
        self.PROVINCE = None  # 主键id
        self.CITY = None  # 所属车次号
        self.REGIONS = None  # 内层剩余宽度
        self.CONTACTNAME = None  # 外层剩余宽度
        self.CONTACTPHONE = None  # 所属层数
        self.ISNOSHORTOVER = None  # 每层内侧高度
        self.REMARK = None  # 每层外侧高度
        self.CREATTIME = None  # 内侧装配货物
        self.STATUS = None  # 外侧装配货物
        self.ALTERTIME = None  # 装配的货物
        self.WAINTFORDELNUMBER = None  # 创建时间
        self.WAINTFORDELWEIGHT = None  # 更新时间
        self.CANSENDNUMBER = None  # 所属车次号
        self.CANSENDWEIGHT = None  # 内层剩余宽度
        self.CALCULATETIME = None  # 外层剩余宽度
        self.end_point = None  # 所属层数
        self.line_name = None  # 每层内侧高度
        self.record_day = None  # 每层外侧高度
        self.prod_kind_price_out = None
        if stock:
            self.set_attr(stock)
