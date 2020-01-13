# -*- coding: utf-8 -*-
# Description: 订单请求
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13
import json

from flask import request, current_app
from flask_restful import Resource

from app.main.services import order_service, dispatch_service
from app.utils.my_exception import MyException
from app.utils.result import Result


class OrderRoute(Resource):

    # def get(self):
    #     return Result.success_response(order_dao.get_all())
    def post(self):
        """输入订单，返回开单结果
        """
        try:
            json_data = json.loads(request.get_data().decode("utf-8"))
            order = order_service.generate_order(json_data['data'])
            sheets = dispatch_service.dispatch(order)
            return Result.success_response(sheets)
        except MyException as me:
            current_app.logger.info(me.message)
            current_app.logger.exception(me)
            return Result.error_response(me.message)


