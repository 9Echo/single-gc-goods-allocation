# -*- coding: utf-8 -*-
# Description: 获取库存服务
# Created: shaoluyu 2019/11/13
import json

import requests
from flask import current_app


def get_stock():
    """
    获取成都管厂库存
    :return:
    """
    try:
        # 成都管厂库存API
        url = 'http://171.221.245.89:9411/chengdu/weight/getRepertory'
        # 设置请求头
        headers = {
            "Content-Type": "application/json;charset-UTF-8"
        }
        input_dict = {
            "length": 1000000,
            "page": 1,
            "itemid": "",
            "requestCompanyId": "C000000888",
            "requestCompanyName": "成都管厂物流",
            "requestUserId": "U000000419",
            "requestCompanyType": "GSLX20",
            "requestUserSegmentId": "002"
        }
        res = requests.post(url, data=json.dumps(input_dict), headers=headers, timeout=20)
        if 'data' not in res.json():
            raise RuntimeError('stock data error')
        result = res.json()['data']['list']
        return result
    except Exception as e:
        current_app.logger.info("get_stock_api error")
        current_app.logger.exception(e)










# def get_stock():
#     """
#     获取库存
#     :return:
#     """
    # redis_conn = redis.Redis(connection_pool=redis_pool)
    # lock_id = RedisLock.try_lock(redis_conn, 'stock_lock', wait_time=20)
    # # 拿到锁，获取库存
    # if lock_id:
    #     # 获取Redis库存数据
    #     json_stock_list = redis_conn.get('gc:stocks')
    #     # 如果数据存在
    #     if json_stock_list:
    #         current_app.logger.info('get stock_list from redis')
    #         result_list = json.loads(json_stock_list)
    #         return result_list
    #         # 如果数据过期或被删除
    #     else:
    #         raise RuntimeError('redis data error')
    # else:
    #     raise RuntimeError('redis data error')
    #
    # RedisLock.unlock(redis_conn, 'stock_lock', lock_id)
    # redis_conn.close()
