# -*- coding: utf-8 -*-
# @Time    : 2019/11/19 13:16
# @Author  : Zihao.Liu
from flask_restful import Resource

from app.main.dao.stock_dao import stock_dao
from app.utils.result import Result


class StockRoute(Resource):

    def get(self):
        stocks = stock_dao.get_all()
        result = Result.entity_success(stocks)
        return result.response()