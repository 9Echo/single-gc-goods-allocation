# -*- coding: utf-8 -*-
# Description: 订单请求
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13
import json

from flask import current_app
from flask import request
from flask_restful import Resource

from app.main.dao.order_dao import order_dao
from app.main.services import order_service
from app.utils.result import Result


class OrderRoute(Resource):
    """
    订单请求,返回推荐发货通知单内容
    示例数据格式：
        {
        "data":{
            "customer_id":"customer a",
            "salesman_id":"salesman a",
            "order_items":[
                {
                    "product_type":"黑管",
                    "spec":"100x200x0.5",
                    "quantity":20,
                    "free_pcs":0
                },
                {
                    "product_type":"长管",
                    "spec":"300x200x0.5",
                    "quantity":50,
                    "free_pcs":5
                }
            ]
        }
    }
    """

    def get(self):
        result = Result.entity_success(order_dao.get_all())
        return result.response()

    def post(self):
        """
        获取订单（或列表），返回开单结果
        :return:
        """
        try:
            json_data = json.loads(request.get_data().decode("utf-8"))
            order = order_service.generate_order(json_data['data'])
            result = Result.entity_success(order)
            return result.response()
        except Exception as e:
            current_app.logger.info("json error")
            current_app.logger.exception(e)
            return Result.error_response()


