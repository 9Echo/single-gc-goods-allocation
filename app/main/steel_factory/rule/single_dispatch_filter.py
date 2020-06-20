import redis

from app.main.steel_factory.rule import single_priority_rule, single_layer_rule
from app.main.steel_factory.service import single_stock_service
from app.util.redis.redis_pool import redis_pool
from app.util.redis.reids_lock import RedisLock


def dispatch(truck):
    """
    单车分货模块
    """
    redis_conn = redis.Redis(connection_pool=redis_pool)
    lock_id = RedisLock.try_lock(redis_conn, 'rg_stock_lock', wait_time=20)
    if lock_id:
        try:
            # 获取指定库存
            stock_list = single_stock_service.get_stock(truck)
            # 急发客户轮询，调整库存顺序
            # stock_list = single_priority_rule.filter(stock_list)
            # 生成车次
            load_task = single_layer_rule.layer_filter(stock_list, truck)
            return load_task
        finally:
            RedisLock.unlock(redis_conn, 'rg_stock_lock', lock_id)
    else:
        return None
