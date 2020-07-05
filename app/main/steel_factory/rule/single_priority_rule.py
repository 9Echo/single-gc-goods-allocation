# 催单客户列表
from app.main.steel_factory.service import redis_service


def consumer_filter(stock_list):
    """
    优先级分货规则：
    1.根据催货和超期将货物分为两档
    2.根据客户轮询原则选择本次分货的客户
    3.将本次客户的货排到前面
    4.按照先催货后超期的顺序将排序结果合并
    """
    # 将库存分为催货库存和其他库存
    hurry_stock_list = [stock for stock in stock_list if stock.priority == 1]
    # 如果没有客户催货一级，就对客户催货二级进行轮询
    if not hurry_stock_list:
        hurry_stock_list = [stock for stock in stock_list if stock.priority == 2]
    left_stock_list = stock_list[len(hurry_stock_list):]
    # 构建催货库存字典, 每个客户对应一个库存列表
    hurry_stock_dict = {}
    for stock in hurry_stock_list:
        hurry_stock_dict.setdefault(stock.consumer, []).append(stock)
    # 如果没有催货库存跳过该过滤器
    if len(hurry_stock_dict) == 0:
        return stock_list
    # 更新客户列表，添加新客户
    hurry_consumer_list = update_consumer_list(hurry_stock_list)
    new_hurry_stock_list = []
    first_index = 0
    find_flag = False
    for consumer in hurry_consumer_list:
        if consumer in hurry_stock_dict:
            find_flag = True
            new_hurry_stock_list.extend(hurry_stock_dict[consumer])
        if not find_flag:
            first_index += 1
    # 队列第一次被抽到的客户移到队列末尾
    hurry_consumer_list.append(hurry_consumer_list[first_index])
    hurry_consumer_list.pop(first_index)
    redis_service.set_hurry_consumer_list(hurry_consumer_list)
    # 将重新排序后的催货列表和剩余库存合并
    return new_hurry_stock_list + left_stock_list


def update_consumer_list(hurry_stock_list):
    """
    更新客户优先级列表
    """
    temp_consumer_list = []
    hurry_consumer_list = redis_service.get_hurry_consumer_list()
    # 催货库存中的新客户记录在临时客户列表中，统计完成后将新客户列表插入到催货客户列表首端
    for stock in hurry_stock_list:
        if stock.consumer not in hurry_consumer_list and stock.consumer not in temp_consumer_list:
            temp_consumer_list.append(stock.consumer)
    hurry_consumer_list[0:0] = temp_consumer_list
    return hurry_consumer_list

# if __name__ == '__main__':
#     trucks = truck_service.get_truck()
#     for truck in trucks:
#         print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
#         stock_list = single_stock_service.get_stock(truck)
#         print('Length:' + str(len(stock_list)))
#         stock_list = filter(stock_list)
#         for stock in stock_list:
#             print(stock.consumer)
