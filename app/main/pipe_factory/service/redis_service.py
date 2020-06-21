# -*- coding: utf-8 -*-
# Description: 内存数据库服务
# Created: shaoluyu 2019/12/04
import json

import datetime as datetime
import redis
from flask import current_app
from app.util.redis.redis_pool import redis_pool
from app.main.pipe_factory.entity.delivery_item import DeliveryItem
from app.util.result import Result


def set_delivery_list(delivery_list):
    """
    将推荐装车清单暂存
    :param delivery_list:
    :return:
    """
    try:
        redis_conn = redis.Redis(connection_pool=redis_pool)
        if not delivery_list:
            return Result.error("无数据！")
        batch_no = getattr(delivery_list[0], "batch_no", None)
        if batch_no:
            dict_list = Result.from_entity(delivery_list).data
            json_data = json.dumps(dict_list)
            redis_conn.set(batch_no, json_data, ex=300)
            return Result.info(msg="保存成功")
    except Exception as e:
        current_app.logger.info("set_delivery_list error")
        current_app.logger.exception(e)
    finally:
        redis_conn.close()


def get_delivery_list(batch_no):
    """
    获取对应批次号的发货通知单列表
    :param batch_no:
    :return:
    """
    try:
        redis_conn = redis.Redis(connection_pool=redis_pool)
        json_list = redis_conn.get(batch_no)
        if json_list:
            delivery_list = json.loads(json_list)
            items = []
            for i in delivery_list:
                items.extend([DeliveryItem(j) for j in i.get('items')])
            return Result.success(data=items)
        else:
            return None
    except Exception as e:
        current_app.logger.info("get_delivery_list error")
        current_app.logger.exception(e)
    finally:
        redis_conn.close()


hurry_consumer_key = 'hurry_consumer'


def set_hurry_consumer_list(hurry_consumer_list):
    """
    更新催货客户名单
    """
    try:
        redis_conn = redis.Redis(connection_pool=redis_pool)
        if not hurry_consumer_list:
            return Result.error("无数据！")

        json_data = json.dumps(hurry_consumer_list)
        redis_conn.set(hurry_consumer_key, json_data)
        # 设置每天结束时过期
        expire_date = datetime.datetime.combine(datetime.date.today(),
                                                datetime.time(23, 59, 59))
        redis_conn.expireat(hurry_consumer_key, expire_date)
        return True
    except Exception as e:
        current_app.logger.info("set hurry consumer list error")
        current_app.logger.exception(e)
    finally:
        redis_conn.close()


def get_hurry_consumer_list():
    """
    获取催货客户名单
    """
    try:
        redis_conn = redis.Redis(connection_pool=redis_pool)
        json_list = redis_conn.get(hurry_consumer_key)
        if json_list:
            hurry_consumer_list = json.loads(json_list)
            return hurry_consumer_list
        else:
            return []
    except Exception as e:
        current_app.logger.info("get hurry consumer list error")
        current_app.logger.exception(e)
    finally:
        redis_conn.close()


if __name__ == '__main__':
    redis_conn = redis.Redis(connection_pool=redis_pool)
    redis_conn.delete(hurry_consumer_key)