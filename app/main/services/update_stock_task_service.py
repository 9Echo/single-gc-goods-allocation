# -*- coding: utf-8 -*-
# Description: Redis连接池
# Created: shaoluyu 2019/11/13
import json

import redis
import requests
from flask import current_app

from app.main.redis_pool import redis_pool
from app.utils.reids_lock import RedisLock


def update_stock():
    """
    定时获取最新库存，更新Redis中库存
    :return:
    """
    try:
        redis_conn = redis.Redis(connection_pool=redis_pool)
        lock_id = RedisLock.try_lock(redis_conn, 'stock_lock', wait_time=20)
        if lock_id:
            result = get_stock_api()
            json_data = json.dumps(result)
            # 将数据放入Redis，默认保存在0分片，数据保存在gc下
            redis_conn.set('gc:stocks', json_data)
        else:
            raise RuntimeError()
    except Exception as e:
        current_app.logger.info("update_stock miss")
        current_app.logger.exception(e)
    finally:
        RedisLock.unlock(redis_conn, 'stock_lock', lock_id)
        redis_conn.close()


def get_stock_api():
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
            raise RuntimeError('redis data error')
        result = res.json()['data']['list']
        return result
    except Exception as e:
        current_app.logger.info("get_stock_api error")
        current_app.logger.exception(e)
