# -*- coding: utf-8 -*-
# Description: 订单请求
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13
import json
import multiprocessing
from multiprocessing import Manager

from flask import request, current_app
from flask_restful import Resource

from app.main.services import order_service, dispatch_service as dispatch_service_spec
from app.task.optimize_task.services import dispatch_service as dispatch_service_optimize
from app.task.pulp_task.services import dispatch_service as dispatch_service_weight
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
                order = order_service.generate_order(json_data['data'])
                # order["items"]
                # manager = Manager()
                # return_dict = manager.dict()
                # p = multiprocessing.Pool(2)
                # p.apply_async(dispatch_service_0.dispatch, (0, return_dict, order))
                # p.apply_async(dispatch_service_1.dispatch, (1, return_dict, order))
                # p.close()  # 关闭进程池，关闭后po不再接收新的请求
                # p.join()  # 等待pool中所有子进程执行完成，必须放在close语句之后
                # print(return_dict.values())
                sheets_1, product_weight1 = dispatch_service_spec.dispatch(order)
                sheets_2, product_weight2 = dispatch_service_weight.dispatch(order)
                sheets_3, product_weight3 = dispatch_service_optimize.dispatch(order)
                product_info_before = test_dispatch_service.get_json_before(order)
                product_info_after1, car_info1 = test_dispatch_service.get_product_info_after(sheets_1)
                product_info_after2, car_info2 = test_dispatch_service.get_product_info_after(sheets_2)
                product_info_after3, car_info3 = test_dispatch_service.get_product_info_after(sheets_3)
                error1 = test_dispatch_service.judge_info(product_info_before, product_info_after1, car_info1, product_weight1)
                error2 = test_dispatch_service.judge_info(product_info_before, product_info_after2, car_info2, product_weight2)
                error3 = test_dispatch_service.judge_info(product_info_before, product_info_after3, car_info3, product_weight3)
                print(error1)
                print(error2)
                print(error3)
                # result_dict = {'spec_first': sheets_1, 'weight_first': sheets_2, 'recommend_first': sheets_3}
                return Result.success_response(sheets_1 + sheets_2 + sheets_3)
        except MyException as me:
            current_app.logger.error(me.message)
            current_app.logger.exception(me)
            return Result.error_response(me.message)


