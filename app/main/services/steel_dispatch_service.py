# -*- coding: utf-8 -*-
# Description: 钢铁配货服务
# Created: shaoluyu 2020/03/12
import copy
from typing import List, Dict, Any
from app.main.entity.load_task import LoadTask
from app.main.entity.stock import Stock
from app.main.services import stock_service
from app.main.services import generate_excel_service
from app.task.pulp_task.analysis.rules import pulp_solve
from app.utils.enum_util import LoadTaskType, DispatchType
from app.utils.generate_id import TrainId
from model_config import ModelConfig


def dispatch() -> List[LoadTask]:
    """
    车辆配货
    :param :
    :return:
    """
    """
    步骤：
    1 将单条库存数据满足标载条件[31,33]的数据直接生成车次，并搜索满足一装一卸的可拼的其他货物，拼到该车次，其中包含超期或催货标为急发车次，并且类型为一装一卸
    2 按照优先发运、最新挂单时间进行正序排序
    3 选择第一条作为目标数据，将除第一条其余数据中出库仓库和区县与其相同或卸货地址与其相同的数据筛选出来作为待选集
    4 按照优先级将待选集与目标数据利用背包进行匹配，使重量最大化，匹配成功（总量在[31,33]）生成车次，标注是否急发和类型，匹配不成功放入甩货列表，
    优先级依次为：一装一卸，两装一卸（同区仓库），两装一卸(不同区仓库),一装两卸
    """

    load_task_list = list()
    # 库存信息获取
    stock_list: List[Stock] = stock_service.deal_stock()
    # 标载车次列表
    standard_stock_list = list(
        filter(lambda x: x.Actual_weight >= ModelConfig.RG_MIN_WEIGHT, stock_list))
    # 普通车次列表
    general_stock_list = list(
        filter(lambda x: x.Actual_weight < ModelConfig.RG_MIN_WEIGHT, stock_list))
    # 标载车次拼凑一装一卸小件货物
    for standard_stock in standard_stock_list:
        # 可拼车列表
        compose_list = list()
        # 车次剩余载重
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - standard_stock.Actual_weight
        # 筛选符合拼车条件的库存列表
        filter_list = list(filter(lambda x: x.Warehouse_out == standard_stock.Warehouse_out
                                            and x.Address == standard_stock.Address
                                            and x.Actual_weight <= surplus_weight
                                            and x.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(
            standard_stock.Big_product_name), general_stock_list))
        # 如果有，按照surplus_weight为约束进行匹配
        if filter_list:
            compose_list, value = goods_filter(filter_list, surplus_weight)
        # 生成车次数据
        load_task_list.extend(
            create_load_task(compose_list + [standard_stock], TrainId.get_id(), LoadTaskType.TYPE_1.value))
    if general_stock_list:
        general_stock_dict: Dict[int, Stock] = dict()
        for i in general_stock_list:
            general_stock_dict[i.Stock_id] = i
        first_surplus_stock_dict = dispatch_filter(general_stock_dict, load_task_list, DispatchType.FIRST)
        surplus_stock_dict = dispatch_filter(first_surplus_stock_dict, load_task_list, DispatchType.SECOND)
        # 分不到标载车次的部分，甩掉，生成一个伪车次加明细
        if surplus_stock_dict:
            load_task_list.extend(create_load_task(list(surplus_stock_dict.values()), -1, LoadTaskType.TYPE_5.value))
        # load_task_list = merge_result(load_task_list)
        return load_task_list


def first_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask], dispatch_type) -> \
        Dict[int, Stock]:
    """
    一装一卸筛选器
    :param dispatch_type:
    :param general_stock_dict:
    :param load_task_list:
    :return:
    """
    result_dict = dict()
    while general_stock_dict:
        # 取第一个
        stock_id = list(general_stock_dict.keys())[0]
        temp_stock = general_stock_dict.get(stock_id)
        # 约束
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if
                       v.Warehouse_out == temp_stock.Warehouse_out and v.Address == temp_stock.Address
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        if filter_dict:
            temp_list = split(filter_dict)
            # 选中的列表
            compose_list, value = goods_filter(temp_list, surplus_weight)
            if dispatch_type is DispatchType.FIRST:
                if (value + temp_stock.Actual_weight) >= ModelConfig.RG_MIN_WEIGHT:
                    calculate(compose_list, general_stock_dict, load_task_list, temp_stock, LoadTaskType.TYPE_1.value)
                    continue
            else:
                if value >= ModelConfig.RG_MIN_WEIGHT:
                    calculate(compose_list, general_stock_dict, load_task_list, None, LoadTaskType.TYPE_1.value)
                    continue
        general_stock_dict.pop(stock_id, 404)
        result_dict[stock_id] = temp_stock
    return result_dict


def second_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask], dispatch_type) -> \
        Dict[int, Stock]:
    """
    两装一卸（同区仓库）筛选器
    :param dispatch_type:
    :param general_stock_dict:
    :param load_task_list:
    :return:
    """
    result_dict = dict()
    while general_stock_dict:
        # 取第一个
        stock_id = list(general_stock_dict.keys())[0]
        temp_stock = general_stock_dict.get(stock_id)
        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        warehouse_out_group: List[str] = list()
        for group in ModelConfig.RG_WAREHOUSE_GROUP:
            if temp_stock.Warehouse_out in group:
                warehouse_out_group = group
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if v.Address == temp_stock.Address
                       and v.Warehouse_out in warehouse_out_group
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        if filter_dict:
            warehouse_out_list: List[str] = list()
            for i in filter_dict.values():
                if i.Warehouse_out not in warehouse_out_list:
                    warehouse_out_list.append(i.Warehouse_out)
            for warehouse_out in warehouse_out_list:
                if warehouse_out != temp_stock.Warehouse_out:
                    temp_dict = {k: v for k, v in filter_dict.items() if
                                 v.Warehouse_out == warehouse_out or v.Warehouse_out == temp_stock.Warehouse_out}
                    temp_list = split(temp_dict)
                    # 选中的列表
                    compose_list, value = goods_filter(temp_list, surplus_weight)
                    if dispatch_type is DispatchType.FIRST:
                        if (value + temp_stock.Actual_weight) >= ModelConfig.RG_MIN_WEIGHT:
                            calculate(compose_list, general_stock_dict, load_task_list, temp_stock,
                                      LoadTaskType.TYPE_2.value)
                            is_error = False
                            break
                    else:
                        if value >= ModelConfig.RG_MIN_WEIGHT:
                            calculate(compose_list, general_stock_dict, load_task_list, None,
                                      LoadTaskType.TYPE_2.value)
                            is_error = False
                            break
        if is_error:
            general_stock_dict.pop(stock_id, 404)
            result_dict[stock_id] = temp_stock
    return result_dict


def third_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask], dispatch_type) -> \
        Dict[int, Stock]:
    """
    两装一卸（非同区仓库）筛选器
    :param dispatch_type:
    :param general_stock_dict:
    :param load_task_list:
    :return:
    """
    result_dict = dict()
    while general_stock_dict:
        # 取第一个
        stock_id = list(general_stock_dict.keys())[0]
        temp_stock = general_stock_dict.get(stock_id)
        # 拆分成件的stock列表

        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if v.Address == temp_stock.Address
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        if filter_dict:
            warehouse_out_list: List[str] = list()
            for i in filter_dict.values():
                if i.Warehouse_out not in warehouse_out_list:
                    warehouse_out_list.append(i.Warehouse_out)
            for warehouse_out in warehouse_out_list:
                if warehouse_out != temp_stock.Warehouse_out:
                    temp_dict = {k: v for k, v in filter_dict.items() if
                                 v.Warehouse_out == warehouse_out or v.Warehouse_out == temp_stock.Warehouse_out}
                    temp_list = split(temp_dict)
                    # 选中的列表
                    compose_list, value = goods_filter(temp_list, surplus_weight)
                    if dispatch_type is DispatchType.FIRST:
                        if (value + temp_stock.Actual_weight) >= ModelConfig.RG_MIN_WEIGHT:
                            calculate(compose_list, general_stock_dict, load_task_list, temp_stock,
                                      LoadTaskType.TYPE_3.value)
                            is_error = False
                            break
                    else:
                        if value >= ModelConfig.RG_MIN_WEIGHT:
                            calculate(compose_list, general_stock_dict, load_task_list, None,
                                      LoadTaskType.TYPE_3.value)
                            is_error = False
                            break
        if is_error:
            general_stock_dict.pop(stock_id, 404)
            result_dict[stock_id] = temp_stock
    return result_dict


def fourth_deal_general_stock(general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask], dispatch_type) -> \
        Dict[int, Stock]:
    """
    一装两卸筛选器
    :param dispatch_type:
    :param general_stock_dict:
    :param load_task_list:
    :return:
    """
    result_dict = dict()
    while general_stock_dict:
        # 取第一个
        stock_id = list(general_stock_dict.keys())[0]
        temp_stock = general_stock_dict.get(stock_id)
        is_error = True
        surplus_weight = ModelConfig.RG_MAX_WEIGHT - temp_stock.Actual_weight \
            if dispatch_type is DispatchType.FIRST else ModelConfig.RG_MAX_WEIGHT
        if dispatch_type is DispatchType.FIRST:
            general_stock_dict.pop(stock_id)
        filter_dict = {k: v for k, v in general_stock_dict.items() if
                       v.Warehouse_out == temp_stock.Warehouse_out and v.End_point == temp_stock.End_point
                       and v.Piece_weight <= surplus_weight
                       and v.Big_product_name in ModelConfig.RG_COMMODITY_GROUP.get(temp_stock.Big_product_name)}
        if filter_dict:
            address_list: List[str] = list()
            for i in filter_dict.values():
                if i.Address not in address_list:
                    address_list.append(i.Address)
            for address in address_list:
                if address != temp_stock.Address:
                    temp_dict = {k: v for k, v in filter_dict.items() if
                                 v.Address == address or v.Address == temp_stock.Address}
                    temp_list = split(temp_dict)
                    # 选中的列表
                    compose_list, value = goods_filter(temp_list, surplus_weight)
                    if dispatch_type is DispatchType.FIRST:
                        if (value + temp_stock.Actual_weight) >= ModelConfig.RG_MIN_WEIGHT:
                            calculate(compose_list, general_stock_dict, load_task_list, temp_stock,
                                      LoadTaskType.TYPE_4.value)
                            is_error = False
                            break
                    else:
                        if value >= ModelConfig.RG_MIN_WEIGHT:
                            calculate(compose_list, general_stock_dict, load_task_list, None,
                                      LoadTaskType.TYPE_4.value)
                            is_error = False
                            break
        if is_error:
            general_stock_dict.pop(stock_id, 404)
            result_dict[stock_id] = temp_stock
    return result_dict


def calculate(compose_list: List[Stock], general_stock_dict: Dict[int, Stock], load_task_list: List[LoadTask],
              temp_stock: Any, load_task_type: str):
    """
    重量计算
    :param compose_list:
    :param general_stock_dict:
    :param load_task_list:
    :param temp_stock:
    :param load_task_type:
    :return:
    """
    temp_dict = dict()
    # 选中的stock按照stock_id分类
    for compose_stock in compose_list:
        temp_dict.setdefault(compose_stock.Stock_id, []).append(compose_stock)
    new_compose_list = list()
    if temp_stock:
        new_compose_list.append(temp_stock)
    for k, v in temp_dict.items():
        # 获取被选中的原始stock
        general_stock = general_stock_dict.get(k)
        stock = v[0]
        stock.Actual_number = len(v)
        stock.Actual_weight = len(v) * stock.Piece_weight
        new_compose_list.append(stock)
        general_stock.Actual_number -= len(v)
        general_stock.Actual_weight = general_stock.Actual_number * general_stock.Piece_weight
        if general_stock.Actual_number == 0:
            general_stock_dict.pop(k)
    # 生成车次数据
    load_task_list.extend(
        create_load_task(new_compose_list, TrainId.get_id(), load_task_type))


def goods_filter(general_stock_list: List[Stock], surplus_weight: int) -> (List[Stock], int):
    """
    背包过滤方法
    :param surplus_weight:
    :param general_stock_list:
    :return:
    """
    compose_list = list()
    weight_list = ([item.Actual_weight for item in general_stock_list])
    value_list = copy.deepcopy(weight_list)
    result_index_list, value = pulp_solve.pulp_pack(weight_list, None, value_list, surplus_weight)
    for index in sorted(result_index_list, reverse=True):
        compose_list.append(general_stock_list[index])
        general_stock_list.pop(index)
    # 数据返回
    return compose_list, value


def create_load_task(stock_list: List[Stock], load_task_id, load_task_type) -> List[LoadTask]:
    """
    车次创建方法
    :param stock_list:
    :param load_task_id:
    :param load_task_type:
    :return:
    """
    total_weight = sum(i.Actual_weight for i in stock_list)
    all_product = set([i.Big_product_name for i in stock_list])
    remark = []
    for product in all_product:
        remark += ModelConfig.RG_VARIETY_VEHICLE[product]
    remark = set(remark)
    load_task_list = list()
    for i in stock_list:
        load_task = LoadTask()
        load_task.load_task_id = load_task_id
        load_task.total_weight = total_weight / 1000
        load_task.weight = i.Actual_weight / 1000
        load_task.count = i.Actual_number
        load_task.city = i.City
        load_task.end_point = i.End_point
        load_task.commodity = i.Small_product_name
        load_task.notice_num = i.Delivery
        load_task.oritem_num = i.Order
        load_task.standard = i.specs
        load_task.sgsign = i.mark
        load_task.outstock_code = i.Warehouse_out
        load_task.instock_code = i.Warehouse_in
        load_task.load_task_type = load_task_type
        load_task.big_commodity = i.Big_product_name
        load_task.receive_address = i.Address
        load_task.remark = ",".join(remark)
        load_task.parent_load_task_id = i.Parent_stock_id
        if i.Priority == 0:
            load_task.priority = "客户催货"
        elif i.Priority == 1:
            load_task.priority = "超期库存"
        else:
            load_task.priority = ""
        load_task_list.append(load_task)
    return load_task_list


def split(temp_dict: Dict[int, Stock]):
    """
    拆分到单件
    :param temp_dict:
    :return:
    """
    # 拆分成件的stock列表
    temp_list: List[Stock] = list()
    for i in temp_dict.values():
        for j in range(i.Actual_number):
            copy_stock = copy.deepcopy(i)
            copy_stock.Actual_number = 1
            copy_stock.Actual_weight = i.Piece_weight
            temp_list.append(copy_stock)
    return temp_list


def dispatch_filter(general_stock_dict, load_task_list, dispatch_type):
    """

    :param general_stock_dict:
    :param load_task_list:
    :param dispatch_type:
    :return:
    """
    first_result_dict = first_deal_general_stock(general_stock_dict, load_task_list, dispatch_type)
    second_result_dict = second_deal_general_stock(first_result_dict, load_task_list, dispatch_type)
    third_stock_dict = third_deal_general_stock(second_result_dict, load_task_list, dispatch_type)
    surplus_stock_dict = fourth_deal_general_stock(third_stock_dict, load_task_list, dispatch_type)
    return surplus_stock_dict


def merge_result(load_task_list: list):
    """合并结果中load_task_id相同的信息

    Args:
        load_task_list: load_task的列表
    Returns:

    Raise:

    """
    result_dic = {}
    last_result = []
    for task in load_task_list:
        if (task.load_task_id, task.parent_load_task_id) not in result_dic:
            result_dic[(task.load_task_id, task.parent_load_task_id)] = []
        result_dic[(task.load_task_id, task.parent_load_task_id)].append(task)
    for res in result_dic:
        # 同一个(load_task_id,parent_load_task_id)的load_task列表
        res_list = result_dic[res]
        if len(res_list) > 1:
            sum_list = [(i.weight, i.count) for i in res_list]
            sum_weight = sum(i[0] for i in sum_list)
            sum_count = sum(i[1] for i in sum_list)
            res_list[0].weight = sum_weight
            res_list[0].count = sum_count
        last_result.append(res_list[0])
    return last_result


if __name__ == '__main__':
    result = dispatch()
    generate_excel_service.generate_excel(result)
