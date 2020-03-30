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
from app.utils.result import Result


class OrderRoute(Resource):

    @staticmethod
    def post():
        """输入订单，返回开单结果
        """
        if request.get_data():
            json_data = json.loads(request.get_data().decode("utf-8"))
            # 数据初始化
            order = order_service.generate_order(json_data['data'])
            # 规格优先
            sheets_1 = dispatch_service_spec.dispatch(order)
            # 重量优先
            # sheets_2 = dispatch_service_weight.dispatch(order)
            # 综合
            # sheets_3 = dispatch_service_optimize.dispatch(order)
            return Result.success_response(sheets_1)
