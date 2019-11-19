# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:12
# @Author  : Zihao.Liu
from flask import current_app

from app.main.dao.base_dao import BaseDao
from app.main.db_pool import db_pool_trans_plan
import traceback
from app.main.entity.delivery_sheet import DeliverySheet
from app.utils.date_util import get_now_str


class DeliverySheetDao(BaseDao):
    def get(self):
        return

    def insert(self, delivery):
        try:
            sql = """
                insert into db_trans_plan.t_ga_delivery_sheet(delivery_no,
                                                              batch_no,
                                                              data_address,
                                                              total_quantity,
                                                              free_pcs,
                                                              total_pcs,
                                                              weight,
                                                              create_time) 
                value(%s,%s,%s,%s,%s,%s,%s,%s)
            """
            value = tuple([delivery.delivery_no, delivery.batch_no, delivery.data_address, delivery.total_quantity, delivery.free_pcs,
                             delivery.total_pcs, delivery.weight, get_now_str()])
            self.execute(sql, value)
        except Exception as e:
            traceback.print_exc()
            current_app.logger.error("delivery_sheet_dao_insert error")

    def update(self):
        try:
            pass

        except Exception as e:
            traceback.print_exc()
            current_app.logger.error("delivery_sheet_dao_update error")


delivery_sheet_dao = DeliverySheetDao()