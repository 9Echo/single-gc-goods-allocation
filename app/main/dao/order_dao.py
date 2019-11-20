# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:10
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
import traceback

from flask import current_app

from app.main.dao.base_dao import BaseDao
from app.main.entity.order import Order
from app.main.entity.order_item import OrderItem
from app.utils.date_util import get_now_str


class OrderDao(BaseDao):

    def get_all(self):
        sql = "select od.*, odi.*, odi.rid as irid, odi.create_time as ict, odi.update_time as iut from t_ga_order od " \
              "left join t_ga_order_item odi on od.order_id=odi.order_id " \
              "order by od.rid"
        results = self.select_all(sql)
        order_dict = {}
        # 将订单项结果合并到订单中
        for row in results:
            if not order_dict.__contains__(row['order_id']):
                order_dict[row['order_id']] = Order(row)
            if row['irid'] is not None:
                row['rid'] = row['irid']
                row['create_time'] = row['ict']
                row['update_time'] = row['iut']
                order_dict[row['order_id']].order_items.append(OrderItem(row))
        return [order for order in order_dict.values()]

    def insert(self, order):
        try:
            # 主表
            sql_main = """
                insert into 
                t_ga_order(
                order_id,
                customer_id,
                salesman_id,
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
                      for item in order.order_items]
            self.executemany(sql_item, values)
        except:
            traceback.print_exc()
            current_app.logger.error("order_dao error")


order_dao = OrderDao()
