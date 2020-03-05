# -*- coding: utf-8 -*-
# Description: 确认发货通知单
# Created: shaoluyu 2019/12/12
from app.analysis.rules import compose_filter
from app.main.dao.compose_dao import compose_dao
from app.main.entity.delivery_item import DeliveryItem
from app.main.entity.delivery_sheet import DeliverySheet


# def generate_delivery(delivery_list_data):
#     """
#     根据json数据生成对应的发货通知单
#     """
#     delivery_model_list = []
#     for delivery in delivery_list_data:
#         delivery_model = DeliverySheet(delivery)
#         delivery_model_list.append(delivery_model)
#
#     return delivery_model_list
from app.utils.aop_util import set_weight


@set_weight
def compose(delivery_list_data):
    """
    拼单推荐逻辑
    :param delivery_list_data:
    :return:
    """
    delivery_dict_list = compose_filter.filter(delivery_list_data)
    if delivery_dict_list:
        return [DeliverySheet(i) for i in delivery_dict_list]
    else:
        return None