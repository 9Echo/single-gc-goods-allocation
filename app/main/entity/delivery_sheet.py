# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:23
# @Author  : Zihao.Liu
from app.main.entity.base_entity import BaseEntity


class DeliverySheet(BaseEntity):
    """发货通知单"""

    def __init__(self, delivery_sheet=None):
        """
            暂时都把字段添加了,注释在上面的是新添加的，有几个含义相同单名字不同的已经注释了，可参考修改
        """
        self.rid = None  # 主键id
        self.delivery_no = None  # 发货通知单号
        self.load_task_id = None  # 所属车次号
        self.batch_no = None  # 批次号
        self.status = None  # 状态 0：待确认 1：已确认
        self.data_address = None  # 数据来源
        self.items = []  # 发货通知单子单
        self.total_quantity = None  # 总件数
        self.free_pcs = None  # 散根数
        self.total_pcs = None  # 总根数
        # # 总件数
        # self.order_j = None
        # # 散根数
        # self.order_g = None
        # # 总根数
        # self.order_zg00 = None
        self.weight = None  # 理重
        # # 理重
        # self.order_cal = None
        self.order_no = None  # 订单id
        self.doc_type = None  # 开单员id
        # # 录入人ID-前端传入
        # self.doctype = None
        self.lrr = None  # 开单员
        # # 录入人即开单员名字首字母-前端传入
        # self.lrr = None
        self.customer_id = None  # 客户id
        self.salesorg = None  # 销售部门id
        self.salesman_id = None  # 销售员id
        # # 销售部门ID-前端传入
        # self.salesorg = None
        # # 销售员ID-前端传入
        # self.slsman = None
        self.create_time = None  # 创建时间
        self.update_time = None  # 更新时间
        # # 创建时间
        # self.crted_date = None
        # # 更新时间
        # self.upted_date = None
        # HL
        self.corpid = None
        # 出入库标记
        self.i_o = None
        # 确认发货通知单后查询开单序号表分配单号
        self.docuno = None
        # 客户公司简称-直接取值，开单时通过请求信息拿到
        self.org_unit = None
        # CRTED_DATE 的年月日
        self.trx_date = None
        # 0.00
        self.trx_qty = None
        # 0.00
        self.trx_amt = None
        # 0
        self.trx_zg00 = None
        # LRR
        self.upted_by = None
        # 仓库
        self.f_whs = None
        # 垛号
        self.f_loc = None
        # 0
        self.trx_j = None
        # 0
        self.trx_g = None
        # 估重合计
        self.order_twe = None
        # 贷款合计
        self.order_amt = None
        # 0.00 运费合计
        self.fee_order = None
        # 空着
        self.note = None
        # N
        self.dibz = None
        if delivery_sheet:
            self.set_attr(delivery_sheet)

