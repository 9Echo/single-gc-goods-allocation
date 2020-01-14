# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 16:17
# @Author  : Zihao.Liu
from flask import request, current_app, jsonify
from flask_restful import Resource

from app.main.services.compose_service import generate_delivery, compose
from app.utils.my_exception import MyException
from app.utils.result import Result


class ComposeRoute(Resource):
    """
    拼单推荐接口
    """
    @staticmethod
    def post():
        """进行拼货推荐"""
        try:
            if request.get_data():
                # 获取输入参数（发货通知单列表）
                delivery_list_data = request.get_json(force=True).get('items')  # 入参是json
                if delivery_list_data:
                    delivery_list = generate_delivery(delivery_list_data)
                    result_delivery_list = compose(delivery_list)
                    return Result.success_response(result_delivery_list)
                else:
                    return Result.error_response('数据为空！')
        except MyException as me:
            current_app.logger.error(me.message)
            current_app.logger.exception(me)
            return Result.error_response(me.message)




