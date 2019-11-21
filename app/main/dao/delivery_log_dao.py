# -*- coding: utf-8 -*-
# @Time    : 2019/11/19 14:12
# @Author  : shaoluyu
import traceback
from flask import current_app

from app.main.dao.base_dao import BaseDao
from app.utils.date_util import get_now_str


class DeliveryLogDao(BaseDao):

    def insert(self, log_insert_list):
        try:
            sql = """
                insert into db_trans_plan.t_ga_delivery_log(delivery_no,
                                                            delivery_item_no,
                                                            op,
                                                            quantity_before,
                                                            quantity_after,
                                                            free_pcs_before,
                                                            free_pcs_after,
                                                            create_time) 
                value(%s,%s,%s,%s,%s,%s,%s,%s)
            """
            values = [tuple([item[0], item[1], item[2], item[3],
                           item[4], item[5], item[6], get_now_str()]) for item in log_insert_list]
            self.executemany(sql, values)
        except Exception as e:
            traceback.print_exc()
            current_app.logger.error("delivery_sheet_dao_insert error")


delivery_log_dao=DeliveryLogDao()