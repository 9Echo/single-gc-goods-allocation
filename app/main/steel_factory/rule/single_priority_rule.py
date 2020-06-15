def filter(stock):
    """
    优先级分货规则：
    1.根据催货和超期将货物分为两档
    2.每档根据最后挂单时间依次排序
    3.按照先催货后超期的顺序将排序结果合并
    """
    return stock