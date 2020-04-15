# -*- coding: utf-8 -*-
# @Time    :
# @Author  : shaoluyu
from app.main.entity.base_entity import BaseEntity


class LoadTask(BaseEntity):
    """车次类"""

    def __init__(self):
        self.load_task_id = None  # 所属车次号
        self.items = []  # 明细
        self.weight = 0
        self.city = None
        self.end_point = None
