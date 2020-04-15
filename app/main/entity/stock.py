# -*- coding: utf-8 -*-
# @Time    : 2020/03/31
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class Stock(BaseEntity):
    """
    钢厂库存类
    """

    def __init__(self, stock=None):
        self.id = None
        self.NOTICENUM = None
        self.SALEDEPT = None
        self.SALEMANAGER = None
        self.PRODCOMPANY = None
        self.PURCHUNIT = None
        self.ENDCUSTMER = None
        self.MOTHERNUM = None
        self.ORITEMNUM = None
        self.DEVPERIOD = None
        self.DELIWAREHOUSE = None
        self.TRANSWAY = None
        self.COMMODITYNAME = None
        self.PACK = None
        self.QUALITY = None
        self.MATERIAL = None
        self.STANDARD = None
        self.THICKNESS = None
        self.WIDTH = None
        self.LENGTH = None
        self.DELIWARE = None
        self.PORTNUM = None
        self.ADDRESS = None
        self.DETAILADDRESS = None
        self.PROVINCE = None
        self.CITY = None
        self.REGIONS = None
        self.CONTACTNAME = None
        self.CONTACTPHONE = None
        self.ISNOSHORTOVER = None
        self.REMARK = None
        self.CREATTIME = None
        self.STATUS = None
        self.ALTERTIME = None
        self.WAINTFORDELNUMBER = None
        self.WAINTFORDELWEIGHT = None
        self.CANSENDNUMBER = None
        self.CANSENDWEIGHT = None
        self.CALCULATETIME = None
        self.end_point = None
        self.line_name = None
        self.record_day = None
        self.prod_kind_price_out = None
        if stock:
            self.set_attr(stock)
