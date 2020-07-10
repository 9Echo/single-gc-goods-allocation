# -*- coding: utf-8 -*-
# Description:
# Created: liujiaye  2020/07/10
from typing import List
from app.main.steel_factory.entity.stock import Stock


def filter(stock_list: List[Stock]):
    stock_dic = {
        "tail": [],
        "lock": [],
        "huge": []
    }
    for s in stock_list:
        # 获取重量下限
        min_weight = 29000

        if s.actual_weight >= min_weight:
            stock_dic["huge"].append(s)
        else:
            # (可发件数+待产件数)*件重<重量下限
            future_sum_weight=(s.actual_number+)*s.piece_weight
            if future_sum_weight<=min_weight:
                stock_dic["tail"].append(s)
            else:
                if s.waint_fordel_weight>150000:
                    stock_dic["huge"].append(s)
                else:
                    stock_dic["lock"].append(s)

