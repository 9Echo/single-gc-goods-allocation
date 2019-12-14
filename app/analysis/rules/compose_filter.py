# -*- coding: utf-8 -*-
# @Time    : 2019/12/12
# @Author  : shaoluyu
from app.analysis.rules import compose_weight_rule
from app.main.dao.compose_dao import compose_dao
from app.utils.code import ResponseCode
from app.utils.my_exception import MyException


def filter(delivery_list: list):
    """
    拼单推荐逻辑
    :param delivery_list:
    :return:
    """

    # 客户列表
    customer_id_list = []
    # 发货通知单号列表
    delivery_no_list = []
    # 公司id
    company_id = ''
    # 现有重量
    weight = 0
    for i in delivery_list:
        if not company_id:
            company_id = i.company_id
        if i.delivery_no:
            delivery_no_list.append(i.delivery_no)
        customer_id_list.append(i.customer_id)
        weight += float(i.weight)
    if not delivery_no_list:
        raise MyException('提货单号为空！', ResponseCode.Error)
    if not customer_id_list:
        raise MyException('客户为空！', ResponseCode.Error)
    delivery_dict_list = compose_dao.get_compose_delivery(company_id, customer_id_list, delivery_no_list)
    if delivery_list:
        return compose_weight_rule.filter(delivery_dict_list, weight)
    else:
        return None