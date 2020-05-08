# -*- coding: utf-8 -*-
# @Time    : 2020/03/31
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class Stock(BaseEntity):
    """
    钢厂库存类
    """

    def __init__(self, stock=None):
        self.Stock_id = None  # Id
        self.Delivery = None  # 发货通知单
        self.Order = None  # 订单号
        self.Priority = None  # 优先发运
        self.Consumer = None  # 收货用户
        self.Small_product_name = None  # 品名名称
        self.Big_product_name = None  # 品名
        self.mark = None  # 牌号
        self.specs = None  # 规格
        self.Warehouse_out = None  # 出库仓库
        self.Province = None  # 省份
        self.City = None  # 城市
        self.End_point = None  # 终点
        self.Logistics = None  # 物流公司类型
        self.Pack_form = None  # 包装形式
        self.Address = None  # 卸货地址
        self.Latest_order_time = None  # 最新挂单时间
        self.Delivery_date = None  # 合同约定交货日期
        self.Actual_weight: int = 0  # 实际可发重量
        self.Actual_number: int = 0  # 实际可发件数
        self.Piece_weight: int = 0  # 件重
        self.Warehouse_in = None  # 入库仓库
        self.longitude = None   # 经度
        self.latitude = None   # 纬度
        self.Address2 = None    # 合并卸货地址

        if stock:
            self.set_attr(stock)
