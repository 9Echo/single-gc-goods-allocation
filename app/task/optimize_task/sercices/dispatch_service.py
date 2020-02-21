# -*- coding: utf-8 -*-
# @Time    : 2020/02/01
# @Author  : shaoluyu
import math

from app.main.entity.delivery_item import DeliveryItem
from app.main.entity.delivery_sheet import DeliverySheet
from app.task.optimize_task.analysis.rules import scipy_optimize
from app.utils import weight_calculator
from model_config import ModelConfig


def dispatch(order):
    """根据订单执行分货
    """
    delivery_items = []
    for item in order.items:
        di = DeliveryItem()
        di.product_type = item.product_type
        di.spec = item.spec
        di.quantity = item.quantity
        di.free_pcs = item.free_pcs
        di.item_id = item.item_id
        di.material = item.material
        di.f_whs = item.f_whs
        di.f_loc = item.f_loc
        di.max_quantity = ModelConfig.ITEM_ID_DICT.get(di.item_id[:3])
        di.volume = di.quantity / di.max_quantity if di.max_quantity else 0
        di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)
        di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)
        # 如果遇到计算不出来的明细，返回0停止计算
        if di.weight == 0:
            sheet = DeliverySheet()
            sheet.weight = '0'
            sheet.items = [di]
            return [sheet]
        # 如果该明细有件数上限并且单规格件数超出，进行切单
        delivery_items.append(di)
    # 定义常量值
    one_volume = []
    one_weight = []
    order_j = []
    max_weight = 32.5
    max_volume = ModelConfig.MAX_VOLUME
    total_weight = 0
    # 计算总重量、最大件数、单件重量、件数信息
    for i in delivery_items:
        # 总重量
        total_weight += i.weight
        one_volume.append(1 / i.max_quantity if i.max_quantity else 1 / 10000)
        one_weight.append(weight_calculator.calculate_weight(i.product_type, i.item_id, 1, 0) / 1000)
        order_j.append(i.quantity)
    # 车次等于总重量除以最大载重量
    car_count = math.ceil(total_weight / 1000 / max_weight)
    # 品种规格数量
    product_type_count = len(delivery_items)
    # 矩阵元素个数等于品种数*车次数
    # count = car_count * product_type_count
    scipy_optimize.my_minimize(one_volume, one_weight, order_j, max_weight, max_volume, (car_count, product_type_count))
