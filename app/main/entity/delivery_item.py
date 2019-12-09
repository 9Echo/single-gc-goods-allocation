# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:25
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class DeliveryItem(BaseEntity):
    """发货通知单子项"""

    def __init__(self, delivery_item=None):
        """
        暂时都把字段添加了,注释在上面的是新添加的，有几个含义相同单名字不同的已经注释了，可参考修改
        """
        self.rid = None  # 主键id
        self.delivery_no = None  # 发货通知单主单号
        self.delivery_item_no = None  # 子单号
        self.order_no = None  # 订单号
        self.product_type = None  # 产品类型
        self.item_id = None   # 物资代码
        self.spec = None  # 产品规格
        self.gh00 = None  # 材质
        self.weight = None  # 产品重量
        self.weightone = None  # 根重
        self.warehouse = None  # 仓库信息
        self.loc_id = None  # 库位信息
        # # 仓库 warehouse
        # self.f_hws = None
        # # 垛号 loc_id
        # self.f_loc = None
        self.quantity = None  # 总数
        self.free_pcs = None  # 散根数
        self.total_pcs = None  # 总根数
        # # 件数
        # self.order_j = None
        # # 散根数
        # self.order_g = None
        # # 总根数
        # self.order_zg00 = None
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        # 创建时间 create_time
        self.crted_date = None
        # 更新时间 等于create_time
        self.upted_date = None
        # HL
        self.corpid = None
        # 出入库标记
        self.i_o = None
        # 录入人ID-前端传入
        self.doctype = None
        # 提货单号-前端传入
        self.docuno = None
        # 序号1,2,3
        self.lno = None
        # 客户公司简称-前端传入
        self.org_unit = None
        # CRTED_DATE 取年月日
        self.trx_date = None
        # n
        self.lot_no = None
        # 单位kg
        self.uom_id = None
        # 录入人首字母-前端传入
        self.lrr = None
        # 销售部门-前端传入
        self.salesorg = None
        # 销售员-前端传入
        self.slsman = None
        # LRR
        self.upted_by = None
        # 物资代码大类 ITEMA.CLASSID(CATEGORIES.CATEGORY_ID)
        self.catno = None
        # ??数字或字母
        self.subcls = None
        # 备注
        self.bz00 = None
        # N
        self.dibz = None
        # t 单位 吨
        self.order_dw = None
        # 1000.00 物料单位转换
        self.uomrate = None
        # 1
        self.validzl = None
        # n
        self.quality = None
        # n
        self.maker = None
        # n
        self.rkrq = None
        # n
        self.zllevel = None
        # n
        self.packagespec = None
        # n
        self.htno = None
        # n
        self.custname = None
        # 空值
        self.dgwidth = None
        # 空值
        self.dgheight = None
        # 空值
        self.dglength = None
        if delivery_item:
            self.set_attr(delivery_item)
