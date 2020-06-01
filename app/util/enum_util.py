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
    三次筛选匹配
    """
    # 急发卷类优先分货类型
    FIRST = 1
    # 目标货物整体分货类型
    SECOND = 2
    # 目标货物拆散分货类型
    THIRD = 3

