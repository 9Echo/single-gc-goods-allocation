# -*- coding: utf-8 -*-
# Description: 定时更新库存
# Created: shaoluyu 2019/11/13
import json

import redis
import requests
from flask import current_app

from app.main.redis_pool import redis_pool
from app.utils.reids_lock import RedisLock


# def update_stock():
#     """
#     定时获取最新库存，更新Redis中库存
#     :return:
#     """
    # try:
    #     redis_conn = redis.Redis(connection_pool=redis_pool)
    #     lock_id = RedisLock.try_lock(redis_conn, 'stock_lock', wait_time=20)
    #     if lock_id:
    #         result = get_stock_api()
    #         json_data = json.dumps(result)
    #         # 将数据放入Redis，默认保存在0分片，数据保存在gc下
    #         redis_conn.set('gc:stocks', json_data)
    #     else:
    #         raise RuntimeError()
    # except Exception as e:
    #     current_app.logger.info("update_stock miss")
    #     current_app.logger.exception(e)
    # finally:
    #     RedisLock.unlock(redis_conn, 'stock_lock', lock_id)
    #     redis_conn.close()



