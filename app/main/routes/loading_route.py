# -*- coding: utf-8 -*-
# Description: 配载图请求
# Created: zhouwentao 2020/03/19
import json

from flask import request, current_app
from flask_restful import Resource

from app.main.services import order_service,sheet_service, dispatch_service as dispatch_service_spec
from app.task.optimize_task.services import dispatch_service as dispatch_service_optimize
from app.task.pulp_task.services import dispatch_service as dispatch_service_weight
from app.utils.my_exception import MyException
from app.utils.result import Result
from app.main.services.loading_sequence_service1 import loading
import turtle as t


class LoadingRoute(Resource):

    @staticmethod
    def post():
        """输入sheets，返回配载方案
        """
        if request.get_data():
            json_data = json.loads(request.get_data().decode("utf-8"))
            # 数据初始化
            # order=order_service.generate_order(json_data['data'])
            sheets = sheet_service.generate_sheets(json_data['data'])
            # 规格优先
            # sheets = dispatch_service_spec.dispatch(order)
            loading_result = loading(sheets, [12000, 2400, 1500])
            # draw_product(a[0][0], t, "in")
            print(loading_result)
            return Result.success_response(loading_result)
