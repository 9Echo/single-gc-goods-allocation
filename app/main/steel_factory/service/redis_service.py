import json
import datetime as datetime
import redis
from flask import current_app
from app.util.redis.redis_pool import redis_pool
from app.util.result import Result

hurry_consumer_key = 'hurry_consumer'


def set_hurry_consumer_list(hurry_consumer_list):
    """
    更新催货客户名单
    """
    redis_conn = None
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
        if redis_conn:
            redis_conn.close()


def get_hurry_consumer_list():
    """
    获取催货客户名单
    """
    redis_conn = None
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
        if redis_conn:
            redis_conn.close()


# if __name__ == '__main__':
# redis_conn = redis.Redis(connection_pool=redis_pool)
# redis_conn.delete(hurry_consumer_key)
