from typing import List, Any, Dict

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.rule.create_load_task_rule import create_load_task
from app.util.generate_id import TrainId


def calculate(compose_list: List[Stock], general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask],
              temp_stock: Any, load_task_type: str):
    """
    重量计算
    :param compose_list:
    :param general_stock_dict:
    :param load_task_list:
    :param temp_stock:
    :param load_task_type:
    :return:
    """
    temp_dict = dict()
    # 选中的stock按照stock_id分类
    for compose_stock in compose_list:
        temp_dict.setdefault(compose_stock.Stock_id, []).append(compose_stock)
    new_compose_list = list()
    if temp_stock:
        new_compose_list.append(temp_stock)
    for k, v in temp_dict.items():
        # 获取被选中的原始stock
        general_stock = general_stock_dict.get(k)
        stock = v[0]
        stock.Actual_number = len(v)
        stock.Actual_weight = len(v) * stock.Piece_weight
        new_compose_list.append(stock)
        general_stock.Actual_number -= len(v)
        general_stock.Actual_weight = general_stock.Actual_number * general_stock.Piece_weight
        if general_stock.Actual_number == 0:
            general_stock_dict.pop(k)
    # 生成车次数据
    load_task_list.extend(
        create_load_task(new_compose_list, TrainId.get_id(), load_task_type))
