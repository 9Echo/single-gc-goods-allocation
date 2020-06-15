from app.main.steel_factory.rule import single_priority_rule, single_layer_rule


def dispatch(stocks: list, trucks: list):
    """
    单车分货模块
    """
    load_task_list = []
    for truck in trucks:
        stocks = single_priority_rule.filter(stocks)
        load_task = single_layer_rule.filter(stocks, truck.weight)
        load_task_list.append(load_task)
    return load_task_list




