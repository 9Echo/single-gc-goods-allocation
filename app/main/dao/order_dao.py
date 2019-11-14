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
        # 获取连接
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        sql_main = """
            insert into 
            t_ga_order(
            order_id,
            dest,
            customer_id,
            saleman_id,
            create_time
            ) value (
            '{}',
            '{}',
            '{}',
            '{}',
            now()
            )
            """.format(
            order.order_id,
            order.dest,
            order.customer_id,
            order.salesman_id
        )
        sql_item = """
        insert into
                t_ga_order_item(
                order_id,
                product_type,
                spec,
                quantity,
                number,
                create_time
                ) value 
        """
        value_list = []
        for i in order.order_item:

            value_list.append("""
               (
                '{}',
                '{}',
                '{}',
                 {},
                 {},
                now()
                )
        """.format(
                i.order_id,
                i.product_type,
                i.spec,
                i.quantity,
                i.number
            ))
        sql_item += ','.join(value_list)
        cursor.execute(sql_main)
        cursor.execute(sql_item)
        conn.commit()
    except Exception as e:
        conn.rollback()
        current_app.logger.info("order_dao error")
        current_app.logger.exception(e)
    finally:
        cursor.close()
        conn.close()



