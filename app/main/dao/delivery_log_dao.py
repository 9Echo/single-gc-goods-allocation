# -*- coding: utf-8 -*-
# @Time    : 2019/11/19 14:12
# @Author  : shaoluyu
from app.main.dao.base_dao import BaseDao


class DeliveryLogDao(BaseDao):

    def insert(self, ):
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
            value = tuple([delivery.delivery_no, delivery.batch_no, delivery.data_address, delivery.total_quantity,
                           delivery.free_pcs,
                           delivery.total_pcs, delivery.weight, get_now_str()])
            self.execute(sql, value)
        except Exception as e:
            traceback.print_exc()
            current_app.logger.error("delivery_sheet_dao_insert error")