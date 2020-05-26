from typing import List

from app.main.steel_factory.entity.load_task import LoadTask
from app.main.steel_factory.entity.stock import Stock
from model_config import ModelConfig


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
        load_task.latest_order_time = i.Latest_order_time
        # 得到翻转优先级的字典
        dic_priority = dict((val, key) for key, val in ModelConfig.RG_PRIORITY.items())
        if i.Priority not in dic_priority:
            load_task.priority = ""
        else:
            load_task.priority = dic_priority[i.Priority]
        load_task_list.append(load_task)
    return load_task_list
