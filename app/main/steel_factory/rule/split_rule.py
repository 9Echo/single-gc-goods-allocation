import copy
from typing import Dict, List
from app.main.steel_factory.entity.stock import Stock


def split(temp_dict: Dict[int, Stock]):
    """
    拆分到单件
    :param temp_dict:
    :return:
    """
    # 拆分成件的stock列表
    temp_list: List[Stock] = list()
    for i in temp_dict.values():
        for j in range(i.actual_number):
            copy_stock = copy.deepcopy(i)
            copy_stock.actual_number = 1
            copy_stock.actual_weight = i.piece_weight
            temp_list.append(copy_stock)
    return temp_list
