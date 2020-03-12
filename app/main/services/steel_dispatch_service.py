# -*- coding: utf-8 -*-
# Description: 钢铁配货服务
# Created: shaoluyu 2020/03/12
from app.main.entity.delivery_sheet import DeliverySheet
from app.main.services import stock_service
from app.task.pulp_task.analysis.rules import pulp_solve
from model_config import ModelConfig


def dispatch(vehicle):
    """
    车辆配货
    :param vehicle:
    :return:
    """
    # 根据车辆条件获取库存
    stock_list = stock_service.get_stock(vehicle)
    # 过滤库存，调用算法进行配货
    return goods_filter(stock_list)


def goods_filter(stock_list):
    """
    货物按照逾期时间倒序排序，选出第一个
    1 选出与第一个同一收货地的数据，并且出库仓库不超过两个
    if 有数据：
        将数据进行背包，约束条件有重量、件数，价值是重量
    else:
        选出与第一个同一出库仓库的数据，并且收货地址不超过两个
        if 有数据：
            将数据进行背包，约束条件有重量、件数，价值是重量
        else:
            将stock_list去除第一个，回到第一步操作，以此类推
    :param stock_list:
    :return:
    """
    # 提取优先考虑的货物列表

    # 数据格式处理，进行背包处理
    weight_list = []
    quantity_list = []
    value_list = []
    result_index_list = pulp_solve.pulp_pack(weight_list, quantity_list, value_list, ModelConfig.MAX_WEIGHT)
    # 获取选中的货物，做价值检验

    # 数据返回
    delivery_sheet = DeliverySheet()
    return delivery_sheet
