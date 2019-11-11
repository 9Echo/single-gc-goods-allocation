# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
from app.main.entity.delivery_sheet import DeliverySheet
from app.main.entity.order import Order


def dispatch(order: Order):
    """
    根据订单执行分货
    :param order:
    :return:
    """
    delivery_sheet = DeliverySheet()

    return delivery_sheet
