# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:12
# @Author  : Zihao.Liu
from app.main.db_pool import db_pool_trans_plan
import traceback
import json

from app.main.entity.delivery_sheet import DeliverySheet


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
                                                          weight,
                                                          create_time) 
            values('{}', '{}', '{}', '{}', '{}', '{}', '{}', now())
        """
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        cursor.execute(sql.format(delivery.delivery_no,
                                  delivery.batch_no,
                                  delivery.data_address,
                                  delivery.total_quantity,
                                  delivery.free_pcs,
                                  delivery.total_pcs,
                                  delivery.weight))
        conn.commit()
    except Exception as e:
        print("delivery_sheet_dao_insert is error")
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    insert(DeliverySheet({"delivery_no": "12345",
                          "batch_no": "54321",
                          "data_address": "山东省",
                          "total_quantity": 1,
                          "items": [],
                          "free_pcs": 0,
                          "total_pcs": 12,
                          "weight": "26000",
                          "create_time": "",
                          "update_time": ""}))