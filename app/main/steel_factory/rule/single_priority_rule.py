def filter(stock):
    """
    优先级分货规则：
    1.根据催货和超期将货物分为两档
    2.根据客户轮询原则选择本次分货的客户
    3.将本次客户的货排到前面
    4.按照先催货后超期的顺序将排序结果合并
    """
    return stock

def update_custom_list(stock):
    """
    更新客户优先级列表（一天一次）
    """