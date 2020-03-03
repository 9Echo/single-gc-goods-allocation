# -*- coding: utf-8 -*-
# Description: 订单请求
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13
import json

from flask import request, current_app
from flask_restful import Resource

from app.main.services import order_service, dispatch_service as dispatch_service_spec
from app.task.optimize_task.services import dispatch_service as dispatch_service_optimize
from app.task.pulp_task.services import dispatch_service as dispatch_service_weight
from tests.main.services import dispatch_result_test
from app.utils.my_exception import MyException
from app.utils.result import Result
from tests import test_dispatch_service


class OrderRoute(Resource):

    # def get(self):
    #     return Result.success_response(order_dao.get_all())

    @staticmethod
    def post():
        """输入订单，返回开单结果
        """
        try:
            if request.get_data():
                json_data = json.loads(request.get_data().decode("utf-8"))
                # 数据初始化
                order = order_service.generate_order(json_data['data'])
                # 规格优先
                sheets_1 = dispatch_service_spec.dispatch(order)
                # 重量优先
                sheets_2 = dispatch_service_weight.dispatch(order)
                # 综合
                sheets_3 = dispatch_service_optimize.dispatch(order)
                return Result.success_response(sheets_1 + sheets_2 + sheets_3)
        except MyException as me:
            current_app.logger.error(me.message)
            current_app.logger.exception(me)
            return Result.error_response(me.message)
