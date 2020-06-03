# -*- coding: utf-8 -*-
# @Time    : 2019/11/25
# @Author  : biyushuang
from app.util.base.base_dao import BaseDao


class WeightCalculatorDao(BaseDao):

    def get_data_list_from_table(self, data_list):
        '''
        :return:
        '''
        sql = """select ITEMID,GBGZL,GS_PER from db_inter.t_itema
                where ITEMID in ({}) and ifnull(GBGZL,'') <> '' and ifnull(GS_PER,'') <> ''"""
        values = "'"
        values += "','".join([item.item_id for item in data_list])
        values += "'"
        data = self.select_all(sql.format(values))
        return data


weight_calculator_dao = WeightCalculatorDao()
