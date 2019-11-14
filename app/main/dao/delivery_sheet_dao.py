# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:12
# @Author  : Zihao.Liu
from app.main.db_pool import db_pool_trans_plan
import traceback

def get():
    return


def insert(delivery):
    try:
        sql = """
            insert into db_trans_plan.t_ga_delivery_sheet(delivery_no,
                                                          batch_no,
                                                          data_address,
                                                          total_quantity,
                                                          free_pcs,
                                                          total_pcs,
                                                          create_time) 
            values('{}', '{}', '{}', '{}', '{}', '{}', now())
        """
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        cursor.execute(sql.format(delivery.delivery_no,
                                  delivery.batch_no,
                                  delivery.data_address,
                                  delivery.total_quantity,
                                  delivery.free_pcs))
        conn.commit()
    except Exception as e:
        print("commodity_dao.write_database is error")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()
