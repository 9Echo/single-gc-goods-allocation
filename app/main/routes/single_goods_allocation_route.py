# -*- coding: utf-8 -*-
# Description: 单车配载
# Created: shaoluyu 2020/06/16
import json
from typing import List
from flask import request
from flask_restful import Resource
from app.main.steel_factory.entity.truck import Truck
from app.main.steel_factory.service.truck_service import generate_truck


class SingleGoodsAllocationRoute(Resource):

    @staticmethod
    def post():
        """
        输入车辆信息，返回开单结果
        """

        json_data = json.loads(request.get_data().decode("utf-8"))
        truck_list: List[Truck] = generate_truck(json_data["data"])
