# -*- coding: utf-8 -*-
# Description: 发货通知单确认
# Created: shaoluyu 2019/11/13
# Modified: shaoluyu 2019/11/13


from flask import current_app
from flask import request
from flask_restful import Resource

from app.main.entity.delivery_sheet import DeliverySheet
from app.main.services.confirm_delivery_service import confirm, generate_delivery, update_delviery_sheet
from app.main.services.modify_info_service import modify_info
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
            delivery_list_data = request.get_json(force=True).get('data')  # 入参是json
            print('delivery_data:  ', delivery_list_data)
            # 创建发货通知单实例，初始化属性
            # delivery = DeliverySheet(delivery_data)
            delivery_list = generate_delivery(delivery_list_data)
            # 返回的是Result对象，判断code
            # modify_result = modify_info(delivery_list)
            # 分线程执行
            # threading.Thread(target=update_delviery_sheet, args=(delivery_list,)).start()
            result = update_delviery_sheet(delivery_list)
            return Result.success_response(result)
        except Exception as e:
            current_app.logger.info("json error")
            current_app.logger.exception(e)
            return Result.error_response()