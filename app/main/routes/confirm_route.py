# -*- coding: utf-8 -*-
# Description: 发货通知单确认
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13
from flask import current_app
from flask import request
from flask_restful import Resource
from app.main.services.confirm_delivery_service import confirm
from app.main.services.confirm_delivery_service import generate_delivery
from app.utils.my_exception import MyException
from app.utils.result import Result


class ConfirmRoute(Resource):
    """
       确认发货通知单，扣减库存
       """

    def post(self):
        """
        获取人工确认后的发货通知单
        对比分析保存差异信息
        :return:
        """
        try:
            # 获取输入参数
            delivery_data = request.get_json(force=True).get('data')  # 入参是json
            # 创建发货通知单实例，初始化属性
            if delivery_data:
                delivery_item_list = generate_delivery(delivery_data)
                # 对比
                confirm(delivery_data['company_id'], delivery_item_list)
                return Result.success_response({})
            else:
                return Result.error_response('数据为空！')
        except MyException as me:
            current_app.logger.info(me.message)
            current_app.logger.exception(me)
            return Result.error_response(me.message)
        except Exception as e:
            current_app.logger.info("confirm error")
            current_app.logger.exception(e)
            return Result.error_response()