from enum import Enum


class LoadTaskType(Enum):
    """
    车次类型
    """
    TYPE_1 = "一装一卸"
    TYPE_2 = "两装一卸(同区仓库)"
    TYPE_3 = "两装一卸(非同区仓库)"
    TYPE_4 = "一装两卸"
    TYPE_5 = "甩货"


class DispatchType(Enum):
    """
    两次筛选匹配
    """
    FIRST = 1
    SECOND = 2

