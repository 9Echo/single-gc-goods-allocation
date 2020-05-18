# -*- coding: utf-8 -*-
# Description: 车辆请求
# Created: shaoluyu 2020/03/12
import json
from flask import request
from flask_restful import Resource
from app.main.pipe_factory.service import vehicle_service, steel_dispatch_service
from app.util.result import Result


class VehicleRoute(Resource):

    @staticmethod
    def post():
        """输入车辆信息，返回开单结果
        """
        if request.get_data():
            json_data = json.loads(request.get_data().decode("utf-8"))
            # 数据初始化
            vehicle = vehicle_service.generate_vehicle(json_data.get('data'))
            # 车辆配货
            delivery_sheet = steel_dispatch_service.dispatch(vehicle)
            # 输出
            return Result.success_response(delivery_sheet)

