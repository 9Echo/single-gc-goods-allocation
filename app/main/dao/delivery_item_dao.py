# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:13
# @Author  : Zihao.Liu
from flask import current_app
from app.main.db_pool import db_pool_trans_plan



def get():
    return


def get_by_sheet(sheet_id):
    return


def insert(delivery_item):
    try:
        # 获取连接
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
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
                ) value 
        """
        value_list = []
        for i in delivery_item:

            value_list.append("""
               (
            '{}',
            '{}',
            '{}',
            '{}',
            '{}',
            '{}',
            '{}',
            '{}',
            '{}',
            '{}',
            '{}',
            '{}',
            '{}',
            now()  )
        """.format(
                i.delivery_no,
                i.delivery_item_no,
                i.customer_id,
                i.salesman_id,
                i.dest,
                i.product_type,
                i.spec,
                i.weight,
                i.warehouse,
                i.quantity,
                i.free_pcs,
                i.total_pcs,
                i.create_time
            ))
        sql_item += ','.join(value_list)
        print(sql_item)
        cursor.execute(sql_item)
        conn.commit()
    except Exception as e:
        conn.rollback()
        current_app.logger.info("order_dao error")
        current_app.logger.exception(e)
    finally:
        cursor.close()
        conn.close()
    return


def batch_insert():
    return