# -*- coding: utf-8 -*-
# Description: Redis连接池
# Created: shaoluyu 2019/11/13
import json

import redis
from flask import current_app

from app.main.dao.delivery_item_dao import insert as insert_items
from app.main.dao.delivery_sheet_dao import insert as insert_main
from app.main.redis_pool import redis_pool
from app.utils.code import ResponseCode
from app.utils.reids_lock import RedisLock
from app.utils.result import Result


def confirm(delivery):
    """
        确认发货通知单，获取Redis库存
        :return:
        """
    try:
        redis_conn = redis.Redis(connection_pool=redis_pool)
        lock_id = RedisLock.try_lock(redis_conn, 'stock_lock', wait_time=20)
        # 拿到锁，获取库存
        if lock_id:
            json_stock_list = redis_conn.get('gc:stocks')
            if json_stock_list:
                stock_list = json.loads(json_stock_list)
                # 进行库存更新，库存不足不做更新
                result = subtract_stock(delivery, stock_list)
                # 如果扣减库存成功，重置Redis
                if result.code == ResponseCode.Success:
                    json_data = json.dumps(result)
                    redis_conn.set('gc:stocks', json_data)
                return result

        else:
            return Result.error("销售太火爆了，请重试")

    except Exception as e:
        current_app.logger.info("confirm error")
        current_app.logger.exception(e)
    finally:
        RedisLock.unlock(redis_conn, 'stock_lock', lock_id)
        redis_conn.close()


def subtract_stock(delivery, stock_list):
    """
    根据确认后的发货通知单，扣减库存
    :return:
    """
    try:
        msg = ""
        tag = True
        for i in delivery.items:
            # 过滤出符合品种、规格的库存数据，会出现同品种同规格有多条数据的情况
            list = list(filter(lambda s: s['cname'] == i.product_type and s['spec'] == i.spec, stock_list))
            # 如果没有数据或库存不足
            if len(list) == 0 or int(list[0]['enterJ']) <int(i.quantity) or int(list[0]['enterG']) <int(i.free_pcs):
                msg += "" + i.product_type + "" + i.spec + "库存不足  "
                tag = False
                continue
            #  库存足够的情况下减库存
            else:
                list[0]['enterJ'] = str(int(list[0]['enterJ']) - int(i.quantity))
                list[0]['enterG'] = str(int(list[0]['enterG']) - int(i.free_pcs))
        if tag:

            insert_main(delivery)
            insert_items(delivery.items)
            return Result.success(stock_list)
        else:
            return Result.warn(msg)

    except Exception as e:
        current_app.logger.info("subtract stock error")
        current_app.logger.exception(e)



