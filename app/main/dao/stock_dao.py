# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:11
# @Author  : Zihao.Liu
from app.main.dao.base_dao import BaseDao
from app.main.entity.stock import Stock


class StockDao(BaseDao):

    def get_all(self):
        sql = "select * from t_ga_stock"
        results = self.select_all(sql)
        return [Stock(row) for row in results]


stock_dao = StockDao()