# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
import copy
import json
import threading

import redis
from flask import current_app

from app.analysis.rules.product_type_rule import product_type_filter
from app.analysis.rules.spec_rule import spec_filter
from app.analysis.rules.weight_rule import weight_filter
from app.main.dao.order_dao import insert
from app.main.entity.delivery_sheet import DeliverySheet
from app.main.entity.order import Order
from app.main.redis_pool import redis_pool
from app.utils.result import Result


def dispatch(order: Order):
    """
    根据订单执行分货
    :param order:
    :return:
    """

    try:
        # 记录订单信息，保存到数据库
        threading.Thread(target=insert, args=(order,)).start()
        # 获取当前库存
        stocks = get_stock()
        # 备份订单
        copy_order = copy.deepcopy(order)
        # 经过过滤，得到符合条件的库存
        stocks, new_order = product_type_filter(order, stocks)
        stocks = spec_filter(order, stocks)
        stocks = weight_filter(order, stocks)
        # 创建发货通知单实例，并初始化
        delivery_sheet = DeliverySheet()
        # 执行分货逻辑，将结合订单信息、过滤信息、库存信息得出结果
        print('以下是开单动作、尾货处理、尾货拼货推荐-----------')
        t_dict = {
                 "rid":"c3a61136d3504dca8305b83b531441d2",
                 "delivery_no":"t3-79887",
                 "batch_no":"20191115085233",
                 "data_address":"0030",
                 "items":[{
                 "rid":"beec5585-0742-11ea-bf11-6c92bf5c7f50",
                 "delivery_no":"c3a61136d3504dca8305b83b531441d2",
                 "delivery_item_no":"t3-79887",
                 "customer_id":"scymymygxgs",
                 "salesman_id":"1d",
                 "dest":"山东省",
                 "product_type":"n",
                 "spec":"029140*4.25*6000",
                 "weight":"267807",
                 "warehouse":"热镀库",
                 "loc_id":"6",
                 "quantity":179,
                 "free_pcs":6911,
                 "total_pcs":"267807",
                 "create_time":"",
                 "update_time":""
                },{
                 "rid":"beec5585-0742-11ea-bf11-6c92bf5c7f50",
                 "delivery_no":"c3a61136d3504dca8305b83b531441d2",
                 "delivery_item_no":"t3-79887",
                 "customer_id":"scymymygxgs",
                 "salesman_id":"1d",
                 "dest":"山东省",
                 "product_type":"n",
                 "spec":"029140*4.25*6000",
                 "weight":"267807",
                 "warehouse":"热镀库",
                 "loc_id":"6",
                 "quantity":179,
                 "free_pcs":6911,
                 "total_pcs":"267807",
                 "create_time":"",
                 "update_time":""
                }],
                 "total_quantity":179,
                 "free_pcs":0,
                 "total_pcs":6911,
                 "weight":"267807",
                 "create_time":"",
                 "update_time":""
                }
        return Result.success(t_dict)
    except Exception as e:
        current_app.logger.info("dispatch error")
        current_app.logger.exception(e)


def get_stock():
    """
    获取库存
    :return:
    """
    redis_conn = redis.Redis(connection_pool=redis_pool)
    # 获取Redis库存数据
    json_stock_list = redis_conn.get('gc:stocks')
    # 如果数据存在
    if json_stock_list:
        current_app.logger.info('get stock_list from redis')
        result_list = json.loads(json_stock_list)
        return result_list
        # 如果数据过期或被删除
    else:
        raise RuntimeError('redis data error')

    redis_conn.close()








