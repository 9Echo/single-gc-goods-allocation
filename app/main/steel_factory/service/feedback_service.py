from typing import List

import requests
import json

import config
from app.main.steel_factory.entity.load_task import LoadTask
from flask import current_app


def service(code, msg, result, id_list):
    """接收状态和结果

    Args:

    Returns:

    Raise:

    """
    data = {
        "code": code,
        "msg": msg,
        "truckTasks": []
    }
    for res in result:
        data["truckTasks"].append(data_format(res, id_list))
    url = config.get_active_config().DISPATCH_SERVICE_URL + "/truckTask/createTruckTasks"
    headers = {
        'Content-Type': 'application/json;charset=UTF-8'
    }
    try:
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            current_app.logger.error('调用反馈接口失败,状态码{}'.format(response.status_code))
    except Exception as e:
        current_app.logger.exception(e)
        current_app.logger.error('调用出错！')


def data_format(load_task: LoadTask, id_list: List[str]):
    """将load_task转化成对应接口所需的格式

    Args:

    Returns:

    Raise:

    """
    dic = {
        "companyId": id_list[0],  # 公司id
        "cargoSplitId": id_list[2],  # 分货任务号
        "loadTaskId": load_task.load_task_id,  # 车次号
        "loadTaskType": load_task.load_task_type,  # 装卸类型
        "priorityGrade": load_task.priority_grade,  # 车次优先级
        "totalWeight": load_task.total_weight,  # 总重量
        "city": load_task.city,  # 城市
        "dlvSpotNameEnd": load_task.end_point,
        "pricePerTon": load_task.price_per_ton,
        "totalPrice": load_task.total_price,
        "earliestOrderTime": load_task.latest_order_time,
        "truckTaskDetails": [{
            "loadTaskId": item.load_task_id,
            "cargoSplitId": id_list[2],
            "priority": item.priority,
            "weight": item.weight,
            "count": item.count,
            "city": item.city,
            "dlvSpotNameEnd": item.end_point,
            "bigCommodity": item.big_commodity,
            "commodity": item.commodity,
            "noticeNum": item.notice_num,
            "oritemNum": item.oritem_num,
            "consumer": item.consumer,
            "standard": item.standard,
            "material": item.sgsign,
            "noticeStockinfoId": item.notice_stockinfo_id,
            "deliware": item.instock_code,
            "deliwareHouse": item.outstock_code,
            "detailAddresss": item.receive_address,
            "latestOrderTime": item.latest_order_time
        } for item in load_task.items]
    }
    return dic
