from typing import List

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.load_task_item import LoadTaskItem
from app.main.steel_factory.entity.stock import Stock
from model_config import ModelConfig


def create_load_task(stock_list: List[Stock], load_task_id, load_task_type) -> LoadTask:
    """
    车次创建方法
    :param stock_list:
    :param load_task_id:
    :param load_task_type:
    :return:
    """
    total_weight = sum(i.actual_weight for i in stock_list)
    all_product = set([i.big_commodity_name for i in stock_list])
    remark = []
    for product in all_product:
        remark += ModelConfig.RG_VARIETY_VEHICLE[product]
    remark = set(remark)
    load_task_list = list()
    load_task = LoadTask()
    load_task.load_task_id = load_task_id
    load_task.total_weight = total_weight / 1000
    load_task.load_task_type = load_task_type
    load_task.remark = ",".join(remark)
    for i in stock_list:
        load_task_item = LoadTaskItem()
        load_task_item.weight = i.actual_weight / 1000
        load_task_item.count = i.actual_number
        load_task_item.city = i.city
        load_task_item.end_point = i.dlv_spot_name_end
        load_task_item.commodity = i.commodity_name
        load_task_item.notice_num = i.notice_num
        load_task_item.oritem_num = i.oritem_num
        load_task_item.standard = i.specs
        load_task_item.sgsign = i.mark
        load_task_item.outstock_code = i.deliware_house
        load_task_item.instock_code = i.deliware
        load_task_item.big_commodity = i.big_commodity_name
        load_task_item.receive_address = i.detail_address
        load_task_item.parent_load_task_id = i.parent_stock_id
        load_task_item.latest_order_time = i.latest_order_time
        # 得到翻转优先级的字典
        dic_priority = dict((val, key) for key, val in ModelConfig.RG_PRIORITY.items())
        if i.priority not in dic_priority:
            load_task_item.priority = ""
        else:
            load_task_item.priority = dic_priority[i.priority]
        load_task.items.append(load_task_item)
    return load_task
