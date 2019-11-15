# -*- coding: utf-8 -*-
# Description: 发货通知单确认
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13


from flask import current_app, jsonify
from flask import request
from flask_restful import Resource

from app.main.entity.delivery_sheet import DeliverySheet
from app.main.entity.order import Order
from app.main.services.confirm_delivery_service import confirm
from app.main.services.dispatch_service import dispatch
from app.utils.code import ResponseCode, ResponseMessage
from app.utils.result import Result


class ConfirmRoute(Resource):
    """
       确认发货通知单，扣减库存
       """

    def post(self):
        """
        获取人工确认后的发货通知单
        判断库存是否充足，扣减库存
        将发货通知单写库,有可能也要写入成都数据库
        :return:
        """
        try:
            # print(type(allot_app_input.get('data')))
            # 获取输入参数
            delivery_data = request.get_json(force=True).get('data')  # 入参是json
            # 创建发货通知单实例，初始化属性
            delivery = DeliverySheet(delivery_data)
            result = confirm(delivery)
            return result.response()
        except Exception as e:
            current_app.logger.info("json error")
            current_app.logger.exception(e)
            return Result.error_response()