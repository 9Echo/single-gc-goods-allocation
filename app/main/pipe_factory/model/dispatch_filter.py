import copy

from flask import g, current_app
from app.main.pipe_factory.rule import weight_rule, package_solution
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.main.pipe_factory.rule.lp_problem_solution import create_variable_list, call_pulp_solve
from app.util.code import ResponseCode
from app.util.my_exception import MyException
from model_config import ModelConfig


def spec_filter(delivery_items: list):
    """
    根据过滤规则将传入的发货子单划分到合适的发货单中
    """
    # 返回的提货单列表
    sheets = []
    # 车次号计数器
    task_id = 0
    # 提货单明细列表
    item_list = []
    # 剩余的发货子单
    left_items = delivery_items
    for i in copy.copy(delivery_items):
        # 如果是热镀或者是螺旋取对应的重量上限
        new_max_weight = g.RD_LX_MAX_WEIGHT if i.product_type in ModelConfig.RD_LX_GROUP else g.MAX_WEIGHT
        # 如果发货子单重量比上限小，直接添加，
        if i.weight <= new_max_weight:
            item_list.append(i)
            left_items.remove(i)
    # 如果有超重的子单，进行compose
    while left_items:
        # 每次取第一个元素进行compose,  filtered_item是得到的一个饱和(饱和即已达到重量上限)的子单
        filtered_item, left_items = weight_rule.compose_spec(left_items[0], left_items)
        item_list.append(filtered_item)
    # 上一步filtered_item中可能含有weight为0的子项，为无效子项
    item_list = list(filter(lambda x: x.weight > 0, item_list))
    # 组装子单数据
    # 就是将item_list中的所有货物都使用背包分成发货通知单明细
    while item_list:
        # 是否满载标记
        is_full = False
        weight_cost = []
        for item in item_list:
            weight_cost.append((int(item.weight), float(item.volume), int(item.weight)))
        # 将所有待选集进行背包
        final_weight, result_list = \
            package_solution.dynamic_programming(len(item_list), g.PACKAGE_MAX_WEIGHT, ModelConfig.MAX_VOLUME,
                                                 weight_cost)
        # 如果满足，说明有重量超出背包重量上限的子单，则返回
        if final_weight <= 0:
            raise MyException('package exception', ResponseCode.Error)
        # 如果本次选中的组合价值在合理值范围内，直接赋车次号，不参于后续的操作
        if (g.PACKAGE_MAX_WEIGHT - ModelConfig.PACKAGE_LOWER_WEIGHT) < final_weight < g.PACKAGE_MAX_WEIGHT:
            is_full = True
            task_id += 1
        # 临时明细存放
        temp_item_list = []
        for i in range(len(result_list)):
            if result_list[i] == 1:
                sheet = DeliverySheet()
                # 取出明细列表对应下标的明细
                sheet.items = [item_list[i]]
                # 设置提货单总体积占比
                sheet.volume = item_list[i].volume
                sheet.type = 'spec_first'
                temp_item_list.append(item_list[i])
                if is_full:
                    sheet.load_task_id = task_id
                sheets.append(sheet)
        # 整体移除被开走的明细
        for i in temp_item_list:
            item_list.remove(i)

    return sheets, task_id

def weight_filter(delivery_item_weight_list,new_max_weight):
    weight_list, volume_list, value_list = create_variable_list(delivery_item_weight_list)
    sheets = call_pulp_solve(weight_list, volume_list, value_list, delivery_item_weight_list, new_max_weight)
    return sheets

def optimize_filter(delivery_items: list, task_id=0):
    """
    根据过滤规则将传入的发货子单划分到合适的发货单中
    """
    # 返回的提货单列表
    sheets = []
    # 提货单明细列表
    item_list = []
    # 剩余的发货子单
    left_items = delivery_items
    new_max_weight = 0
    # 遍历明细列表，如果一个子单的重量不到重量上限，则不参与compose
    for i in copy.copy(delivery_items):
        if i.product_type in ModelConfig.RD_LX_GROUP:
            new_max_weight = g.RD_LX_MAX_WEIGHT
        if i.weight < (new_max_weight or g.MAX_WEIGHT):
            item_list.append(i)
            left_items.remove(i)
    if left_items:
        left_items.sort(key=lambda i: i.weight, reverse=True)
    # 如果有超重的子单，进行compose
    while left_items:
        # 每次取第一个元素进行compose,  filtered_items是得到的一个饱和(饱和即已达到重量上限)的子单
        filtered_items, left_items = weight_rule.compose_optimize([left_items[0]], left_items)
        # 如果过滤完后没有可用的发货子单则返回
        if not filtered_items:
            break
        item_list.extend(filtered_items)

    while item_list:
        # 是否满载标记
        is_full = False
        weight_cost = []
        for item in item_list:
            weight_cost.append((int(item.weight), float(item.volume), int(item.weight)))
        # 将所有子单进行背包选举
        final_weight, result_list = \
            package_solution.dynamic_programming(len(item_list),
                                                 (new_max_weight or g.PACKAGE_MAX_WEIGHT),
                                                 ModelConfig.MAX_VOLUME, weight_cost)
        if final_weight == 0:
            break
        # temp_item_list = copy.copy(item_list)
        # 如果本次选举的组合重量在合理值范围内，直接赋车次号，不参于后续的操作
        if ((new_max_weight or g.PACKAGE_MAX_WEIGHT) - ModelConfig.PACKAGE_LOWER_WEIGHT) < \
                final_weight < (new_max_weight or g.PACKAGE_MAX_WEIGHT):
            is_full = True
        # 记录体积之和
        # volume = 0
        # 临时明细存放
        temp_item_list = []
        # 临时提货单存放
        temp_sheet_list = []
        for i in range(len(result_list)):
            if result_list[i] == 1:
                sheet = DeliverySheet()
                # 取出明细列表对应下标的明细
                sheet.items = [item_list[i]]
                # 设置提货单总体积占比
                sheet.volume = item_list[i].volume
                sheet.type = 'recommend_first'
                # 累加明细体积占比
                # volume += item_list[i].volume
                # 分别加入临时提货单和明细
                temp_item_list.append(item_list[i])
                temp_sheet_list.append(sheet)
        # 体积占比满足限制赋车次号
        if is_full:
            task_id += 1
            # 批量赋车次号
            for i in temp_sheet_list:
                i.load_task_id = task_id
        sheets.extend(temp_sheet_list)
        # 整体移除被开走的明细
        for i in temp_item_list:
            item_list.remove(i)

    return sheets, task_id

