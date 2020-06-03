import json

from flask import request
from flask_restful import Resource

from app.main.steel_factory.service.dispatch_service import dispatch
from app.util.result import Result


class GoodsAllocationRoute(Resource):

    @staticmethod
    def post():
        """输入订单，返回开单结果
        """
        if request.get_data():
            json_data = json.loads(request.get_data().decode("utf-8"))
            id_list = [json_data["company_id"], json_data["create_id"]]
            dispatch(id_list)
            return Result.success_response()
