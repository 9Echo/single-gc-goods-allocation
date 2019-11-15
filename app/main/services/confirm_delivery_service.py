# -*- coding: utf-8 -*-
# Description: Redis连接池
# Created: shaoluyu 2019/11/13
import copy
import json
import pandas
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
                    json_data = json.dumps(result.data)
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

            # 过滤出发货通知单指定的品种、规格、仓库、库位的库存数据，会出现有多条数据的情况
            data_list = list(filter(lambda s: s['cname'] == i.product_type
                                              and s['spec'] == i.spec
                                              and s['whsDesc'] == i.warehouse
                                              and s['locid'] == i.loc_id, stock_list))
            # 如果扣减库存成功最终返回的list
            new_list = list(filter(lambda s: s['cname'] != i.product_type
                                              and s['spec'] != i.spec
                                              and s['whsDesc'] != i.warehouse
                                              and s['locid'] != i.loc_id, stock_list))
            # 如果没有数据或库存不足
            if len(data_list) == 0 or int(list[0]['enterJ']) < int(i.quantity) or int(list[0]['enterG']) < int(i.free_pcs):
                msg += "" + i.product_type + "" + i.spec + "库存不足  "
                tag = False
                continue
            #  库存足够的情况下减库存
            else:
                # 转换库存量
                def transform(row):
                    row['enterJ'] = int(row['enterJ'])
                    row['enterG'] = int(row['enterG'])
                    return row
                df_data = pandas.DataFrame(data_list)
                df_data.apply(transform, axis=1)
                # 得出库存总件数和总散根数的Series
                series = df_data.sum()
                # 得出剩余件数和散根数
                enter_j = int(series['enterJ']) - int(i.quantity)
                enter_g = int(series['enterG']) - int(i.free_pcs)
                # 创建一个新字典，更新库存
                new_dict = copy.deepcopy(data_list[0])
                new_dict['enterJ'] = str(enter_j)
                new_dict['enterG'] = str(enter_g)
                new_list.append(new_dict)

        if tag:

            insert_main(delivery)
            insert_items(delivery.items)
            return Result.success(new_list)
        else:
            return Result.warn(msg)

    except Exception as e:
        current_app.logger.info("subtract stock error")
        current_app.logger.exception(e)
