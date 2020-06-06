import json

from flask import request, current_app
from flask_restful import Resource

from app.main.steel_factory.service.dispatch_service import dispatch, save_load_task
from app.main.steel_factory.service.stock_service import deal_stock
from app.util.result import Result


class GoodsAllocationRoute(Resource):

    @staticmethod
    def post():
        """输入订单，返回开单结果
        """
        # try:
        #     json_data = json.loads(request.get_data().decode("utf-8"))
        #     id_list = [json_data["company_id"], json_data["create_id"]]
        #     data = json_data["data"]
        #     # 库存处理
        #     stock_list = deal_stock(data)
        #     # 配载
        #     load_task_list = dispatch(stock_list)
        #     # 调用反馈接口，表示成功
        #     pass
        #     # 写库
        #     save_load_task(load_task_list, id_list)
        #     return Result.success_response()
        # except Exception as e:
        #     current_app.logger.exception(e)
        #     # 调用反馈接口,表示错误
        #     pass



