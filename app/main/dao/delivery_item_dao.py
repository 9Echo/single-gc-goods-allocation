# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:13
# @Author  : Zihao.Liu
import traceback

from flask import current_app

from app.main.dao.base_dao import BaseDao
from app.main.db_pool import db_pool_trans_plan
from app.utils.date_util import get_now_str

class DeliveryItemDao(BaseDao):
    def get(self):
        return


    def get_by_sheet(self, sheet_id):
        return


    def insert(self, delivery_item):

        try:

            sql_item = """
                        insert into
                                t_ga_delivery_item(
                                delivery_no,
                                delivery_item_no,
                                customer_id,
                                salesman_id,
                                dest,
                                product_type,
                                spec,
                                weight,
                                warehouse,
                                quantity,
                                free_pcs,
                                total_pcs,
                                create_time
                                ) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
            values = [tuple([item.delivery_no, item.delivery_item_no, item.customer_id, item.salesman_id, item.dest,
                             item.product_type,item.spec,item.weight,item.warehouse,
                             item.quantity, item.free_pcs, item.total_pcs,
                             get_now_str()]) for item in delivery_item]
            self.executemany(sql_item, values)



        except Exception as e:
                current_app.logger.info("delivery_sheet_dao error")
                current_app.logger.exception(e)



    def batch_insert(self):
        return

    def update(self):
        try:
            pass

        except Exception as e:
            traceback.print_exc()
            current_app.logger.error("delivery_item_dao_update error")

delivery_item_dao = DeliveryItemDao()