# 催单客户列表
hurry_custom_list = []


def filter(stock_list):
    """
    优先级分货规则：
    1.根据催货和超期将货物分为两档
    2.根据客户轮询原则选择本次分货的客户
    3.将本次客户的货排到前面
    4.按照先催货后超期的顺序将排序结果合并
    """
    # 将库存分为催货库存和其他库存
    hurry_stock_list = []
    for stock in stock_list:
        if stock.priority == 1:
            hurry_stock_list.append(stock)
    left_stock_list = stock_list[len(hurry_stock_list):]
    # 构建催货库存字典, 每个客户对应一个库存列表
    hurry_stock_dict = {}
    for stock in hurry_stock_list:
        if hurry_stock_dict.__contains__(stock.custom):
            hurry_stock_dict[stock.custom] = []
        else:
            hurry_stock_dict[stock.custom].append(stock)
    # 更新客户列表，添加新客户
    update_custom_list(hurry_stock_list)
    new_hurry_stock_list = []
    for custom in hurry_custom_list:
        new_hurry_stock_list.append(hurry_stock_dict[custom])
    # 队列首位的客户移到队列末尾
    hurry_custom_list.append(hurry_custom_list[0])
    hurry_custom_list.pop(0)
    # 将重新排序后的催货列表和剩余库存合并
    return new_hurry_stock_list.append(left_stock_list)


def update_custom_list(hurry_stock_list):
    """
    更新客户优先级列表
    """
    temp_custom_list = []
    # 催货库存中的新客户记录在临时客户列表中，统计完成后将新客户列表插入到催货客户列表首端
    for stock in hurry_stock_list:
        if not hurry_custom_list.__contains__(stock.custom):
            temp_custom_list.append(stock.custom)
    hurry_custom_list.insert(0, temp_custom_list)

