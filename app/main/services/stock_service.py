# -*- coding: utf-8 -*-
# Description: 获取库存服务
# Created: shaoluyu 2019/11/13
import json

import redis
from flask import current_app

from app.main.redis_pool import redis_pool
from app.utils.reids_lock import RedisLock


def get_stock():
    """
    获取库存
    :return:
    """
    redis_conn = redis.Redis(connection_pool=redis_pool)
    lock_id = RedisLock.try_lock(redis_conn, 'stock_lock', wait_time=20)
    # 拿到锁，获取库存
    if lock_id:
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
    else:
        raise RuntimeError('redis data error')

    RedisLock.unlock(redis_conn, 'stock_lock', lock_id)
    redis_conn.close()
