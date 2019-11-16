# -*- coding: utf-8 -*-
# Description: 订单请求
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13
import json

from flask import current_app, jsonify
from flask import request
from flask_restful import Resource

from app.main.entity.order import Order
from app.main.services.dispatch_service import dispatch
from app.utils.result import Result


class OrderRoute(Resource):
    """
    订单请求,返回推荐发货通知单内容
    """

    def post(self):
        """
        获取订单（或列表），返回开单结果
        :return:
        """
        try:
            # print(type(allot_app_input.get('data')))
            # 获取输入参数
            data = request.get_data().decode('utf-8')
            # data.decode('unicode_escape')

            order_data = json.loads(data)
            # order_data = request.get_json(force=True).get('data')  # 入参是json

            # 创建订单实例，初始化订单属性
            order = Order(order_data['data'])
            # 执行开单，输出结果
            result = dispatch(order)
            return result.response()
        except Exception as e:
            current_app.logger.info("json error")
            current_app.logger.exception(e)
            return Result.error_response()


