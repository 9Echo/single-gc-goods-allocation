# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 16:17
# @Author  : Zihao.Liu
from flask import request
from flask_restful import Resource


class ComposeRoute(Resource):
    """
    拼单推荐接口
    """
    @staticmethod
    def post(order_no):
        """进行拼货推荐"""
        # 获取输入参数（发货通知单）
        delivery_data = request.get_json(force=True).get('data')  # 入参是json




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
