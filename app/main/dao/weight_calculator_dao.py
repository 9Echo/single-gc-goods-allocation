# -*- coding: utf-8 -*-
# @Time    : 2019/11/25
# @Author  : biyushuang
from app.main.dao.base_dao import BaseDao


class WeightCalculatorDao(BaseDao):

    def get_all_data(self):
        sql = """select * 
        from db_trans_plan.t_calculator_item"""
        data = self.select_all(sql)
        return data

    def update_gbgzl(self, update_list):
        sql = """update db_trans_plan.t_calculator_item 
                        set GBGZL = %s
                        where ITEMID = %s and CNAME = %s"""
        values = [(
            item["GBGZL"],
            item["ITEMID"],
            item["CNAME"]) for item in update_list]
        self.executemany(sql, values)
        print("update fininsh!")

    def get_data_from_table(self, cname, itemid):
        '''
        获取t_calculator_item数据
        # 更新t_calculator_item时:
        #   sql = """select * from t_calculator_item
        #            where CNAME = '方矩管' or CNAME = '热镀方矩管'"""
        #   data = self.select_all(sql)
        :return:
        '''
        sql = """select * from t_calculator_item
                where CNAME = %s and ITEMID = %s"""
        values = [cname, itemid]
        data = self.select_all(sql, values)
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