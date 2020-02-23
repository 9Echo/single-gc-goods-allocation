# -*- coding: utf-8 -*-
# Description: 订单请求
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13
import json
import multiprocessing
from multiprocessing import Manager

from flask import request, current_app
from flask_restful import Resource

from app.main.services import order_service, dispatch_service as dispatch_service_0
from app.task.weight_first_task.services import dispatch_service as dispatch_service_1
from app.task.pulp_task.services import dispatch_service as dispatch_service_2
from app.utils.my_exception import MyException
from app.utils.result import Result


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
                # manager = Manager()
                # return_dict = manager.dict()
                # p = multiprocessing.Pool(2)
                # p.apply_async(dispatch_service_0.dispatch, (0, return_dict, order))
                # p.apply_async(dispatch_service_1.dispatch, (1, return_dict, order))
                # p.close()  # 关闭进程池，关闭后po不再接收新的请求
                # p.join()  # 等待pool中所有子进程执行完成，必须放在close语句之后
                # print(return_dict.values())
                sheets_0 = dispatch_service_0.dispatch(order)
                sheets_1 = dispatch_service_1.dispatch(order)
                sheets_2 = dispatch_service_2.dispatch(order)
                return Result.success_response(sheets_2)
        except MyException as me:
            current_app.logger.error(me.message)
            current_app.logger.exception(me)
            return Result.error_response(me.message)
