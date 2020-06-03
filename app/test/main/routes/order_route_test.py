# -*- coding: utf-8 -*-
# Description: 订单请求
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13
import json

from flask import request, current_app
from flask_restful import Resource

from app.main.pipe_factory.service import order_service, dispatch_service as dispatch_service_spec
from app.task.optimize_task.services import dispatch_service as dispatch_service_optimize
from app.task.pulp_task.services import dispatch_service as dispatch_service_weight
from app.test.main.services import dispatch_result_test
from app.util.my_exception import MyException
from app.util.result import Result

class OrderRouteTest(Resource):

    # def get(self):
    #     return Result.success_response(order_dao.get_all())
    @staticmethod
    def post():
        """输入订单，返回开单结果
        """
        try:
            if request.get_data():
                json_data = json.loads(request.get_data().decode("utf-8"))
                order = order_service.generate_order(json_data['data'])

                sheets_1,weight1 = dispatch_service_spec.dispatch_spec(order)
                sheets_2,weight1 = dispatch_service_weight.dispatch(order)
                sheets_3,weight1 = dispatch_service_optimize.dispatch(order)
                spec_results_dict= dispatch_result_test.collect_difference("spec_sheets", sheets_1)
                weight_results_dict= dispatch_result_test.collect_difference("weight_sheets", sheets_2)
                optimize_results_dict= dispatch_result_test.collect_difference("optimize_sheets", sheets_3)
                print("规格优先:")
                for item in spec_results_dict.keys():
                    print(spec_results_dict[item])
                print("\n")
                print("重量优先:")
                for item in weight_results_dict.keys():
                    print(weight_results_dict[item])
                print("\n")
                print("综合优先:")
                for item in optimize_results_dict.keys():
                    print(optimize_results_dict[item])
                print("\n")
                return Result.success_response(sheets_1)
        except MyException as me:
            current_app.logger.error(me.message)
            current_app.logger.exception(me)
            return Result.error_response(me.message)