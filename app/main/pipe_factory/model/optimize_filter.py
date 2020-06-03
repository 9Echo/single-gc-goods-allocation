import copy

import pandas as pd
from flask import g
from app.main.pipe_factory.rule import weight_rule, package_solution
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.main.pipe_factory.service.dispatch_load_task_service import dispatch_load_task_optimize
from app.main.pipe_factory.service.replenish_property_service import replenish_property
from app.util.uuid_util import UUIDUtil

from model_config import ModelConfig

def optimize_filter_max(delivery_items: list, task_id=0):
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


def optimize_filter_min(sheets, min_delivery_item, task_id, order, batch_no):
    """
    小管装填大管车次，将小管按照件数从小到大排序
    若小管不够，分完结束
    若小管装填完所有车次后有剩余，进行背包和遍历
    :param batch_no: 分货批次号
    :param order: 订单
    :param sheets:大管的提货单列表
    :param min_delivery_item:小管的子项列表
    :param task_id:当前分配车次号
    :return: None
    """
    if not sheets:
        # 2、使用模型过滤器生成发货通知单
        min_sheets, task_id = optimize_filter_max(min_delivery_item)
        # 3、补充发货单的属性
        replenish_property(min_sheets, order, batch_no)
        # 为发货单分配车次
        dispatch_load_task_optimize(min_sheets, task_id)
        sheets.extend(min_sheets)
    else:
        min_delivery_item.sort(key=lambda i: i.quantity)
        sheets_dict = [sheet.as_dict() for sheet in sheets]
        df = pd.DataFrame(sheets_dict)
        series = df.groupby(by=['load_task_id'])['weight'].sum().sort_values(ascending=False)
        for k, v in series.items():
            max_weight = 0
            current_weight = v
            # 判断该车次是否下差过大
            current_sheets = list(filter(lambda i: i.load_task_id == k, sheets))
            if current_sheets and current_sheets[0].items:
                if current_sheets[0].items[0].product_type in ModelConfig.RD_LX_GROUP:
                    max_weight = g.RD_LX_MAX_WEIGHT
            if v >= (max_weight or g.MAX_WEIGHT):
                continue
            for i in copy.copy(min_delivery_item):
                # 如果该子项可完整放入
                if i.weight <= (max_weight or g.MAX_WEIGHT) - current_weight:
                    # 当前重量累加
                    current_weight += i.weight
                    # 生成新提货单，归到该车次下
                    new_sheet = DeliverySheet()
                    new_sheet.load_task_id = k
                    new_sheet.volume = i.volume
                    new_sheet.batch_no = batch_no
                    new_sheet.customer_id = order.customer_id
                    new_sheet.salesman_id = order.salesman_id
                    new_sheet.weight = i.weight
                    new_sheet.total_pcs = i.total_pcs
                    new_sheet.type = 'recommend_first'
                    new_sheet.items.append(i)
                    sheets.append(new_sheet)
                    # 移除掉被分配的子项
                    min_delivery_item.remove(i)
                else:
                    i, new_item = \
                        weight_rule.split_item_optimize(i, i.weight - ((max_weight or g.MAX_WEIGHT) - current_weight))
                    if new_item:
                        # 生成新提货单，归到该车次下
                        new_sheet = DeliverySheet()
                        new_sheet.load_task_id = k
                        new_sheet.volume = i.volume
                        new_sheet.batch_no = batch_no
                        new_sheet.customer_id = order.customer_id
                        new_sheet.salesman_id = order.salesman_id
                        new_sheet.weight = i.weight
                        new_sheet.type = 'recommend_first'
                        new_sheet.total_pcs = i.total_pcs
                        new_sheet.items.append(i)
                        # 移除掉被分配的子项
                        min_delivery_item.remove(i)
                        # 将剩余的子项放入子项列表
                        min_delivery_item.insert(0, new_item)
                        sheets.append(new_sheet)
                    break
        # 装填完如果小管还有剩余，进行单独分货
        if min_delivery_item:
            # 2、使用模型过滤器生成发货通知单
            min_sheets, task_id = optimize_filter_max(min_delivery_item, task_id)
            # 3、补充发货单的属性
            for sheet in min_sheets:
                sheet.batch_no = batch_no
                sheet.customer_id = order.customer_id
                sheet.salesman_id = order.salesman_id
                sheet.weight = 0
                sheet.total_pcs = 0
                for di in sheet.items:
                    di.delivery_item_no = UUIDUtil.create_id("di")
                    sheet.weight += di.weight
                    sheet.total_pcs += di.total_pcs
            # 为发货单分配车次
            dispatch_load_task_optimize(min_sheets, task_id)
            sheets.extend(min_sheets)

if __name__ == '__main__':
    pass