# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:12
# @Author  : Zihao.Liu

from app.util.base.base_dao import BaseDao
from app.main.pipe_factory.entity.delivery_item import DeliveryItem
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.util.date_util import get_now_str
from app.main.pipe_factory.dao.delivery_item_dao import delivery_item_dao


class DeliverySheetDao(BaseDao):

    def insert(self, sheet):
        """保存发货单"""
        sql = """insert into db_trans_plan.t_ga_delivery_sheet(
            load_task_id,
            delivery_no,
            `status`,
            customer_id,
            salesman_id,
            weight,
            create_time) value(%s,%s,%s,%s,%s,%s,%s)"""
        values = (
            sheet.load_task_id,
            sheet.delivery_no,
            sheet.status,
            sheet.customer_id,
            sheet.salesman_id,
            sheet.weight,
            get_now_str())
        self.execute(sql, values)
        # 保存发货单项
        if sheet.items:
            from app.main.pipe_factory.dao.delivery_item_dao import delivery_item_dao
            delivery_item_dao.batch_insert(sheet.items)

    def update(self, delivery):
        """更新发货单"""
        sql = """update db_trans_plan.t_ga_delivery_sheet set 
            total_quantity = %s, 
            free_pcs = %s
            where delivery_no = %s"""
        values = (
            delivery.total_quantity,
            delivery.free_pcs,
            delivery.delivery_no)
        self.execute(sql, values)

    def batch_insert(self, sheets):
        """批量保存发货单"""
        sql = """insert into db_trans_plan.t_ga_delivery_sheet(
            load_task_id,
            delivery_no,
            `status`,
            customer_id,
            salesman_id,
            weight,
            create_time) value(%s,%s,%s,%s,%s,%s,%s)"""
        if sheets:
            values = [(
                sheet.load_task_id,
                sheet.delivery_no,
                sheet.status,
                sheet.customer_id,
                sheet.salesman_id,
                sheet.weight,
                get_now_str) for sheet in sheets]
            self.executemany(sql, values)
            for sheet in sheets:
                if sheet.items:
                    delivery_item_dao.batch_insert(sheet.items)


delivery_sheet_dao = DeliverySheetDao()
