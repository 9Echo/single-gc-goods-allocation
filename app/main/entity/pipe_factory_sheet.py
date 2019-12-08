from app.main.entity.base_entity import BaseEntity


class PipeFactorySheet(BaseEntity):
    """管厂格式发货通知单主单

    Args:

    Returns:

    Raise:

    """
    def __init__(self, delivery_sheet=None):
        # HL
        self.corpid = None
        # 出入库标记
        self.i_o = None
        # 录入人ID-前端传入
        self.doctype = None
        # ??未解决 提货单号-前端传入
        self.docuno = None
        # 客户公司简称-1.前端2.通过订单号订单表查出
        self.org_unit = None
        # CRTED_DATE 的年月日
        self.trx_date = None
        # 0.00
        self.trx_qty = None
        # 0.00
        self.trx_amt = None
        # 0
        self.trx_zg00 = None
        # 录入人即开单员名字首字母-前端传入
        self.lrr = None
        # 空着
        self.bbr = None
        # 销售部门ID-前端传入
        self.salesorg = None
        # 销售员ID-前端传入
        self.slsman = None
        # 创建时间
        self.crted_date = None
        # 更新时间
        self.upted_date = None
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
        # 总件数
        self.order_j = None
        # 散根数
        self.order_g = None
        # 总根数
        self.order_zg00 = None
        # 估重合计
        self.order_twe = None
        # 贷款合计
        self.order_amt = None
        # 0.00 运费合计
        self.fee_order = None
        # 空着
        self.note = None
        # ‘空’
        self.pdbz = None
        # N
        self.dibz = None
        # 空值
        self.ywlx = None
        # 理重
        self.order_cal = None
        # 空值
        self.thfs = None
        self.items = []
        if delivery_sheet:
            self.set_attr(delivery_sheet)
       