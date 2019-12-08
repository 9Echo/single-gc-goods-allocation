# coding=utf-8
# creater:chengtao 2019.12.08
# description:管厂子单实体
from app.main.entity.base_entity import BaseEntity


class PipeFactoryItem(BaseEntity):
    """管厂格式发货通知单子单

    Args:

    Returns:

    Raise:

    """
    def __init__(self, delivery_item=None):
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
        # 物资代码item_id
        self.itemid = None
        # 材质
        self.gh00 = None
        # n
        self.lot_no = None
        # 单位kg
        self. uom_id = None
        # 空着
        self.trx_qty = None
        # 空值
        self.prc_in = None
        # 空值
        self.amt_in = None
        # 空着
        self.bzdm = None
        # 空着
        self.jzdm = None
        # 空着
        self.bzrs = None
        # 空着
        self.gss = None
        # 空着
        self.s_date = None
        # 空着
        self.e_date = None
        # 录入人首字母-前端传入
        self.lrr = None
        # 空着
        self.bbr = None
        # 销售部门-前端传入
        self.salesorg = None
        # 销售员-前端传入
        self.slsman = None
        # 创建时间 create_time
        self.crted_date = None
        # 更新时间 等于create_time
        self.upted_date = None
        # LRR
        self.upted_by = None
        # 件数
        self.enter_j = None
        # 散根
        self.enter_g = None
        # 总根数
        self.zg00 = None
        # 物资代码大类 ITEMA.CLASSID(CATEGORIES.CATEGORY_ID)
        self.catno = None
        # ??数字或字母
        self.subcls = None
        # 备注
        self.bz00 = None
        # 仓库 warehouse
        self.f_hws = None
        # 垛号 loc_id
        self.f_loc = None
        # 空着
        self.costprc = None
        # ??合同单件重量？？？可先置为空
        self.order_qty = None
        # 空
        self.pdbz = None
        # N
        self.dibz = None
        # 空值
        self.ywlx = None
        # t 单位 吨
        self.order_dw = None
        # 1000.00 物料单位转换
        self.uomrate = None
        # 空着
        self.trx_dw = None
        # 1
        self.validzl = None
        # 空着
        self.acno = None
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
        # 件数
        self.order_j = None
        # 散根数
        self.order_g = None
        # 总根数
        self.order_zg00 = None
        # ?? 合同金额？？？先置为空
        self.prc_order = None
        # 空着
        self.fee_order = None
        if delivery_item:
            self.set_attr(delivery_item)