# -*- coding: utf-8 -*-
# Description: 订单请求
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13
import json

from flask import request
from flask_restful import Resource

from app.main.dao.delivery_sheet_dao import delivery_sheet_dao
from app.main.dao.order_dao import order_dao
from app.main.services import order_service, dispatch_service
from app.utils.result import Result


class OrderRoute(Resource):

    def get(self):
        return Result.success_response(order_dao.get_all())

    def post(self):
        """获取订单（或列表），返回开单结果
        示例数据格式：
        {
            "data":{
                "customer_id":"customer a",
                "salesman_id":"salesman a",
                "items":[
                {
                    "product_type":"方矩管",
                    "spec":"058040*040*2.0*6000",
                    "quantity":20,
                    "free_pcs":0
                },
                {
                    "product_type":"热镀",
                    "spec":"02A165*4.25*6000",
                    "quantity":50,
                    "free_pcs":5
                }]
            }
        }
        """
        json_data = json.loads(request.get_data().decode("utf-8"))
        order = order_service.generate_order(json_data['data'])
        delivery = dispatch_service.dispatch(order)
        return Result.success_response(delivery_sheet_dao.get_one(delivery.delivery_no))


