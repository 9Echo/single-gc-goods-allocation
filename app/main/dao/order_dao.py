# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:10
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
import traceback

from flask import current_app

from app.main.dao.base_dao import BaseDao
from app.utils.date_util import get_now_str


class OrderDao(BaseDao):
    def get(self):
        return


    def insert(self, order):
        try:
            # 主表
            sql_main = """
                insert into 
                t_ga_order(
                order_id,
                customer_id,
                saleman_id,
                create_time
                ) value (
                %s,%s,%s,%s
                )
                """
            value = ([order.order_id, order.customer_id, order.salesman_id, get_now_str()])
            self.execute(sql_main, value)
            # 子表
            sql_item = """ 
            insert into
                    t_ga_order_item(
                    order_id,
                    product_type,
                    spec,
                    quantity,
                    free_pcs,
                    create_time
                    ) value(%s,%s,%s,%s,%s,%s)
            """
            values = [tuple([item.order_id, item.product_type, item.spec, item.quantity, item.free_pcs, get_now_str()])
                      for item in order.order_item]
            self.executemany(sql_item, values)
        except:
            traceback.print_exc()
            current_app.logger.error("order_dao error")


orderdao = OrderDao()




