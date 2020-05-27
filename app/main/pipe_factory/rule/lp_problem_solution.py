import copy

from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.task.pulp_task.analysis.rules import pulp_solve
from app.util.uuid_util import UUIDUtil


def create_variable_list(delivery_items):
    """

    :return:
    """
    weight_list = []
    # 每件对应的体积占比
    volume_list = []
    for i in delivery_items:
        weight_list.append(i.weight)
        volume_list.append(i.volume)
    # 构建目标序列
    value_list = copy.deepcopy(weight_list)
    return weight_list, volume_list, value_list


def call_pulp_solve(weight_list, volume_list, value_list, delivery_items, new_max_weight):
    """

    :param delivery_items:
    :param weight_list:
    :param volume_list:
    :param new_max_weight:
    :param value_list:
    :return:
    """
    load_task_id = 0
    batch_no = UUIDUtil.create_id("ba")
    # 结果集
    sheets = []
    while delivery_items:
        load_task_id += 1
        # plup求解，得到选中的下标序列
        result_index_list, value = pulp_solve.pulp_pack(weight_list, volume_list, value_list, new_max_weight)

        #理这里分出来的result_index_list的物资应该合起来是一车上的物品，但是由于可能有不同品类的货，所以不能合并在一张发货单上
        for i in sorted(result_index_list, reverse=True):
            sheet = DeliverySheet()
            item = delivery_items[i]
            sheet.items.append(item)

            # 设置提货单总体积占比
            sheet.volume = item.volume
            sheet.type = 'weight_first'
            #重量优先每次都能分车，所以模型跑完就不用后续分车了
            sheet.load_task_id = load_task_id
            sheets.append(sheet)
            weight_list.pop(i)
            volume_list.pop(i)
            value_list.pop(i)
            delivery_items.pop(i)
    return sheets
