# -*- coding: utf-8 -*-
# Description: 确认发货通知单
# Created: shaoluyu 2019/12/12
from app.main.steel_factory.rule import compose_filter
from app.main.steel_factory.entity.delivery_sheet import DeliverySheet
from app.util.aspect.method_before import set_weight


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
