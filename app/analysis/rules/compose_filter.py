# -*- coding: utf-8 -*-
# @Time    : 2019/12/12
# @Author  : shaoluyu
from app.analysis.rules import compose_weight_rule
from app.main.dao.compose_dao import compose_dao


def filter(delivery_list: list):
    """
    拼单推荐逻辑
    :param delivery_list:
    :return:
    """

    # 客户列表
    customer_id_list = []
    # 公司id
    company_id = ''
    # 现有重量
    weight = 0
    for i in delivery_list:
        company_id = i.company_id if company_id == '' else company_id
        customer_id_list.append(i.customer_id)
        weight += float(i.weight)
    delivery_dict_list = compose_dao.get_compose_delivery(company_id, customer_id_list)
    if delivery_list:
        return compose_weight_rule.filter(delivery_dict_list, weight)
    else:
        return None