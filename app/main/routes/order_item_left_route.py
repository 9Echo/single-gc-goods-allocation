# -*- coding: utf-8 -*-
# @Time    : 2019/11/14 16:46
# @Author  : Zihao.Liu
from flask import request
from flask_restful import Resource

from app.main.dao.order_item_left_dao import order_item_left_dao
from app.main.entity.order_item_left import OrderItemLeft
from app.utils.result import Result


class OrderLeftItemRoute(Resource):

    def get(self):
        return Result.success_response(order_item_left_dao.get_all())

    def post(self):
        item_data = request.get_json(force=True).get('data')
        print(item_data)
        items = [OrderItemLeft(v) for v in item_data]
        order_item_left_dao.batch_insert(items)
        return Result.success_response("操作成功")
