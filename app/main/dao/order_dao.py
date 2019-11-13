# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:10
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
from flask import current_app

from app.main.db_pool import db_pool_trans_plan
from app.main.entity.order import Order


def get():
    return


def insert(order: Order):
    try:
        sql = """
            insert into 
            t_ga_order(
            order_id
            product_type
            spec
            quantity
            dest
            customer_id
            saleman_id
            create_time
            ) value (
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            now()
            )
            """.format(
            order.order_id,
            order.product_type,
            order.spec,
            order.quantity,
            order.dest,
            order.customer_id,
            order.salesman_id
        )
        # 获取连接
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()
        current_app.logger.info("order_dao error")
        current_app.logger.exception(e)
    finally:
        cursor.close()
        conn.close()



