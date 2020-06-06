import requests
import json
from app.main.steel_factory.entity.load_task import LoadTask
from flask import current_app


def service(code, msg, result):
    """接收状态和结果

    Args:

    Returns:

    Raise:

    """
    data = {
        "code": code,
        "msg": msg,
        "datas": []
    }
    for res in result:
        data["datas"].append(data_format(res))
    url = ""
    response = requests.post(url=url,
                             data=json.dumps(data)
                             )
    if code:
        if response.status_code:
            # 调用接口失败
            print("调用接口失败！")
    else:
        # app日志输出？
        print("算法调用失败！{}".format(msg))
        current_app.logger.infor("算法调用失败！{}".format(msg))


def data_format(load_task: LoadTask):
    """将load_task转化成对应接口所需的格式

    Args:

    Returns:

    Raise:

    """
    dic = {
        "company_id": "",  # 公司id
        "cargo_sharing_deal_id": "",  # 分货任务号
        "load_task_id": load_task.load_task_id,  # 车次号
        "load_task_type": load_task.load_task_type,  # 装卸类型
        "priority_grade": load_task.priority_grade,  # 车次优先级
        "total_weight": load_task.total_weight,  # 总重量
        "city": load_task.city,  # 城市
        "dlv_spot_name_end": load_task.end_point,
        "price_per_ton": load_task.price_per_ton,
        "total_price": load_task.total_price,
        "earliest_order_time": load_task.latest_order_time,
        "items": [{
            "load_task_id": item.load_task_id,
            "cargo_sharing_deal_id": "",
            "priority": item.priority,
            "weight": item.weight,
            "count": item.count,
            "city": item.city,
            "dlv_spot_name_end": item.end_point,
            "big_commodity": item.big_commodity,
            "commodity": item.commodity,
            "notice_num": item.notice_num,
            "oritem_num": item.oritem_num,
            "consumer": item.consumer,
            "standard": item.standard,
            "material": "",
            "deliware": item.instock_code,
            "deliware_house": item.outstock_code,
            "detail_addresss": item.receive_address,
            "latest_order_time": item.latest_order_time
        } for item in load_task.items]
    }
    return dic
