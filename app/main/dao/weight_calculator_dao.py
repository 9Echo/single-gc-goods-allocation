# -*- coding: utf-8 -*-
# @Time    : 2019/11/25
# @Author  : biyushuang

import pandas as pd
import traceback
from app.main.dao.base_dao import BaseDao
from app.main.db_pool import db_pool_trans_plan, db_pool_ods


class WeightCalculatorDao(BaseDao):

    def get_data_from_table(self):
        '''
        获取t_calculator_item数据
        # 更新t_calculator_item时，sql加where CNAME = '方矩管' or CNAME = '热镀方矩管'
        :return:
        '''
        sql = """select * from t_calculator_item """

        data = self.select_all(sql)
        return data

    def update_data(self, update_list):
        sql = """update db_trans_plan.t_calculator_item 
                set JM_D = %s
                where ITEMID = %s and CNAME = %s"""
        values = [(
                item["JM_D"],
                item["ITEMID"],
                item["CNAME"]) for item in update_list]
        self.executemany(sql, values)
        print("update fininsh!")

weight_calculator_dao = WeightCalculatorDao()