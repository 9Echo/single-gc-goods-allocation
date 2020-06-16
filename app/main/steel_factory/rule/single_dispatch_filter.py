from typing import List
from app.main.steel_factory.rule import single_priority_rule, single_layer_rule
from app.main.steel_factory.service import single_stock_service


def dispatch(trucks: list):
    """
    单车分货模块
    """
    load_task_list = []
    for truck in trucks:
        stock_list = single_stock_service.get_stock(truck)
        stock_list = single_priority_rule.filter(stock_list)
        load_task = single_layer_rule.filter(stock_list, truck)
        # 更新内存库存信息
        stock_list = single_stock_service.update_stock(load_task, stock_list)
        load_task_list.append(load_task)
    return load_task_list
