# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:12
# @Author  : Zihao.Liu

from app.main.dao.base_dao import BaseDao
from app.main.entity.delivery_item import DeliveryItem
from app.main.entity.delivery_sheet import DeliverySheet
from app.utils.date_util import get_now_str
from app.utils.uuid_util import UUIDUtil
from app.main.dao.delivery_item_dao import delivery_item_dao

class DeliverySheetDao(BaseDao):

    def get_one(self, sheet_id):
        """根据delivery_no查询发货单"""
        sql = "select * from t_ga_delivery_sheet where delivery_no=%s"
        values = (sheet_id,)
        delivery_sheet = DeliverySheet(self.select_one(sql, values))
        # 查询发货单的子发货单
        sql = "select * from t_ga_delivery_item where delivery_no=%s"
        results = self.select_all(sql, values)
        delivery_sheet.items = [DeliveryItem(row) for row in results]
        return delivery_sheet

    def insert(self, delivery):
        # 保存发货单
        sql = """insert into db_trans_plan.t_ga_delivery_sheet(
            load_task_id,
            delivery_no,
            `status`,
            total_quantity,
            total_free_pcs,
            total_pcs,
            weight,
            create_time) value(%s,%s,%s,%s,%s,%s,%s,%s)"""
        values = (
            delivery.load_task_id,
            delivery.delivery_no,
            delivery.status,
            delivery.total_quantity,
            delivery.free_pcs,
            delivery.total_pcs,
            delivery.weight,
            get_now_str())
        self.execute(sql, values)
        # 保存发货单项
        if delivery.items:
            from app.main.dao.delivery_item_dao import delivery_item_dao
            delivery_item_dao.batch_insert(delivery.items)

    def update(self, delivery):
        sql = """update db_trans_plan.t_ga_delivery_sheet set 
            total_quantity = %s, 
            free_pcs = %s
            where delivery_no = %s"""
        values = (
            delivery.total_quantity,
            delivery.free_pcs,
            delivery.delivery_no)
        self.execute(sql, values)

    def batch_insert(self, delivery_list):
        # 保存发货单
        sql = """insert into db_trans_plan.t_ga_delivery_sheet(
            load_task_id,
            delivery_no,
            `status`,
            total_quantity,
            total_free_pcs,
            total_pcs,
            weight,
            create_time) value(%s,%s,%s,%s,%s,%s,%s,%s)"""
        if delivery_list:
            values = [(
                delivery.load_task_id,
                delivery.delivery_no,
                delivery.status,
                delivery.total_quantity,
                delivery.free_pcs,
                delivery.total_pcs,
                delivery.weight,
                get_now_str()) for delivery in delivery_list]
        self.executemany(sql, values)
        for item in delivery_list:
            if item.items:
                delivery_item_dao.batch_insert(item.items)

delivery_sheet_dao = DeliverySheetDao()

if __name__ == "__main__":
    delivery = DeliverySheet()
    delivery.delivery_no = UUIDUtil.create_id("ds")
    delivery.batch_no = UUIDUtil.create_id("batch")
    delivery.status = 0
    delivery.data_address = 00
    delivery.total_quantity = 1000
    delivery.free_pcs = 1000
    delivery.total_pcs = 0
    delivery.weight = 1000
    for i in range(0, 3):
        item = DeliveryItem()
        item.delivery_no = delivery.delivery_no
        item.delivery_item_no = UUIDUtil.create_id("di")
        item.order_no = "abc"
        item.product_type = "方矩管"
        item.spec = "058040*040*2.0*6000"
        item.quantity = 500
        item.free_pcs = 10
        item.total_pcs = 0
        item.warehouse = "方矩库"
        item.weight = 30
        delivery.items.append(item)
    delivery_sheet_dao.insert(delivery)