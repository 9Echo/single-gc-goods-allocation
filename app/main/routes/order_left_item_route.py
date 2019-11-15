# -*- coding: utf-8 -*-
# @Time    : 2019/11/14 16:46
# @Author  : Zihao.Liu
from flask import request
from flask_restful import Resource

from app.main.dao.order_left_item_dao import order_left_item_dao
from app.main.entity.order_left_item import OrderLeftItem
from app.utils.json_util import json_encode
from app.utils.result import Result


class OrderLeftItemRoute(Resource):

    def get(self):
        items = order_left_item_dao.get_all()
        result = Result.success(json_encode(items))
        return result.response()

    def post(self):
        item_data = request.get_json(force=True).get('data')
        print(item_data)
        items = [OrderLeftItem(v) for v in item_data]
        order_left_item_dao.batch_insert(items)
        result = Result.success(json_encode(items))
        return result.response()
