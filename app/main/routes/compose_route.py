# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 16:17
# @Author  : Zihao.Liu
from flask import request, current_app, jsonify
from flask_restful import Resource

from app.main.services.compose_service import generate_delivery, compose
from app.utils.result import Result


class ComposeRoute(Resource):
    """
    拼单推荐接口
    """
    @staticmethod
    def post():
        """进行拼货推荐"""
        try:
            # 获取输入参数（发货通知单列表）
            delivery_list_data = request.get_json(force=True).get('data')  # 入参是json
            if delivery_list_data:
                delivery_list = generate_delivery(delivery_list_data)
                item_list = compose(delivery_list)
                return jsonify({"code": 100, "msg": "成功", "data": item_list})
            else:
                return Result.error_response('数据为空！')
        except Exception as e:
            current_app.logger.info("json error")
            current_app.logger.exception(e)
            return Result.error_response("服务器错误")



    # def generate_delivery_sheet(order):
    #     ds = DeliverySheet()
    #     ds.delivery_no = UUIDUtil.create_id("delivery")
    #     ds.free_pcs = 0
    #     ds.total_quantity = 0
    #     ds.items = []
    #     for orderitem in order.order_item:
    #         di = DeliveryItem()
    #         di.quantity = orderitem.quantity
    #         ds.total_quantity += di.quantity
    #         di.free_pcs = orderitem.free_pcs
    #         ds.free_pcs += di.free_pcs
    #         di.product_type = orderitem.product_type
    #         ds.items.append(di)
    #     return ds
