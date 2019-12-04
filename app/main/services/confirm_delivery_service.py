# -*- coding: utf-8 -*-
# Description: 确认发货通知单
# Created: shaoluyu 2019/11/13
import copy
import json
import threading
from functools import reduce

import pandas
import redis
from flask import current_app

from app.main.dao.delivery_item_dao import delivery_item_dao
from app.main.dao.delivery_sheet_dao import delivery_sheet_dao
from app.main.entity.delivery_item import DeliveryItem
from app.main.redis_pool import redis_pool
from app.utils.code import ResponseCode
from app.utils.reids_lock import RedisLock
from app.utils.result import Result
from app.main.dao.delivery_log_dao import delivery_log_dao
from app.main.entity.delivery_log import DeliveryLog

# test:
import json
import os
from app.main.entity.delivery_sheet import DeliverySheet
import numpy as np
from app.main.services import order_service, dispatch_service


def generate_delivery(delivery_list_data):
    """
    根据json数据生成对应的发货通知单
    """
    delivery_model_list = []
    for delivery in delivery_list_data:
        delivery_model = DeliverySheet(delivery)
        delivery_model.items = []

        for item in delivery['items']:
            delivery_item_model = DeliveryItem(item)
        # delivery_item.delivery_no = delivery.delivery_no
            delivery_model.items.append(delivery_item_model)
        delivery_model_list.append(delivery_model)

    return delivery_model_list


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
                if result.code == ResponseCode.Info:
                    json_data = json.dumps(result.data)
                    redis_conn.set('gc:stocks', json_data)
                    result.data = None
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
                                              and s['itemid'] == i.spec
                                              and s['whsDesc'] == i.warehouse
                                              and s['locid'] == str(i.loc_id), stock_list))

            # 更新stock_list
            stock_list = list(filter(lambda s: s['cname'] != i.product_type
                                              or s['itemid'] != i.spec
                                              or s['whsDesc'] != i.warehouse
                                              or s['locid'] != str(i.loc_id), stock_list))
            # 如果没有数据，也允许开单，并做出提示
            if len(data_list) == 0:
                msg += "品名：" + i.product_type + "规格：" + i.spec + "没有库存  "
                # 管厂逻辑：如果库存没有找到开单的规格，在库存表插入一条库存数据，只有预留库存信息
                tag = False
                continue
            else:
                # 校验发货通知单件数、散根数
                i.quantity = i.quantity if i.quantity is not None else 0
                i.free_pcs = i.free_pcs if i.free_pcs is not None else 0
                # 转换库存量
                def transform(row):
                    row['enterJ'] = int(row['enterJ']) if row['enterJ'] is not None else 0
                    row['enterG'] = int(row['enterG']) if row['enterG'] is not None else 0
                    return row
                df_data = pandas.DataFrame(data_list)
                df_data = df_data.apply(transform, axis=1)
                # 得出库存总件数和总散根数的Series
                series = df_data.sum()
                # 如果库存不足，也允许开单，但做出提示
                if int(series['enterJ']) < int(i.quantity) or int(series['enterG']) < int(i.free_pcs):
                    msg += "品名" + i.product_type + " 规格" + i.spec + " 库存不足，件数剩余"\
                                    +series['enterJ'] +"件，散根剩余：" + series['enterG'] +"根   "
                # 得出剩余件数和散根数
                enter_j = int(series['enterJ']) - int(i.quantity)
                enter_g = int(series['enterG']) - int(i.free_pcs)
                # 创建一个新字典，更新库存
                new_dict = copy.deepcopy(data_list[0])
                new_dict['enterJ'] = str(enter_j)
                new_dict['enterG'] = str(enter_g)
                stock_list.append(new_dict)

        if tag:
            # 这里要改成更新发货通知单主子表,对比数据，将对比有差异的两条数据保存到log表，状态分别为初始状态、确认状态
            # threading.Thread(target=delivery_sheet_dao.insert, args=(delivery,)).start()
            # threading.Thread(target=delivery_item_dao.insert, args=(delivery.items,)).start()
            return Result.info(msg=msg if msg != "" else "成功", data=stock_list)
        else:
            return Result.warn(msg)

    except Exception as e:
        current_app.logger.info("subtract stock error")
        current_app.logger.exception(e)


def update_delviery_sheet(delivery):

    """
    :param:
    :return:
    """
    # 新数据
    delivery_list = [(DeliveryItem(i)) for i in delivery.items]
    # 原数据
    origin_items = delivery_item_dao.get_by_sheet(delivery.delivery_no)
    # 插入列表
    insert_list = list(filter(lambda i: i.delivery_item_no is None, delivery_list))
    # 删除列表
    delete_list = list(filter(lambda i: i.delivery_item_no not in [j.delivery_item_no for j in delivery_list], origin_items))
    # 更新列表
    delivery_update_list = list(filter(lambda i: i.delivery_item_no in [j.delivery_item_no for j in origin_items], delivery_list))
    origin_update_list = list(filter(lambda i: i.delivery_item_no in [j.delivery_item_no for j in delivery_list], origin_items))
    # log表
    log_insert_list = [DeliveryLog({"delivery_no": i.delivery_no, "delivery_item_no": i.delivery_item_no, "op": 1,
                                    "quantity_before": 0, "quantity_after": i.quantity, "free_pcs_before": 0,
                                    "free_pcs_after": i.free_pcs}) for i in insert_list]
    log_delete_list = [DeliveryLog({"delivery_no": i.delivery_no, "delivery_item_no": i.delivery_item_no, "op": 0,
                                    "quantity_before": i.quantity, "quantity_after": 0, "free_pcs_before": i.free_pcs,
                                    "free_pcs_after": 0}) for i in delete_list]
    log_update_list = []
    for i in origin_update_list:
        for j in delivery_update_list:
            if i.delivery_item_no == j.delivery_item_no and i.delivery_no == j.delivery_no:
                if i.quantity !=j.quantity or i.free_pcs != j.free_pcs:
                    log_update_list.append(
                        DeliveryLog({"delivery_no": i.delivery_no, "delivery_item_no": i.delivery_item_no, "op": 2,
                                     "quantity_before": i.quantity, "quantity_after": j.quantity,"free_pcs_before": i.free_pcs,
                                     "free_pcs_after": j.free_pcs}))
    log_insert_list.extend(log_update_list)
    log_insert_list.extend(log_delete_list)
    delivery_sheet = DeliverySheet()
    delivery_sheet.total_quantity = reduce(lambda x, y: x + y, [int(i.quantity) for i in delivery_list])
    delivery_sheet.free_pcs = reduce(lambda x, y: x + y, [int(i.free_pcs) for i in delivery_list])
    delivery_sheet.delivery_no = delivery.delivery_no
    print(delivery_sheet.total_quantity)
    print(delivery_sheet.free_pcs)
    # 数据库操作
    delivery_log_dao.insert(log_insert_list)
    delivery_sheet_dao.update(delivery_sheet)
    delivery_item_dao.batch_insert(insert_list)
    delivery_item_dao.batch_delete(delete_list)
    delivery_item_dao.batch_update(delivery_update_list)


if __name__ == '__main__':
    basedir = os.path.realpath(os.path.dirname(__file__))
    json_path = os.path.join(basedir, "..", "..", "analysis", "analysis", "delivery.json")
    with open(json_path, 'r',encoding='UTF-8') as f:
        datas = json.loads(f.read())
    # 创建发货通知单实例，初化属性
    delivery = DeliverySheet(datas["data"])
    # print(delivery)
    update_delviery_sheet(delivery)
    # ds = delivery_sheet_dao.get_one("ds_70247e800ce711ea9e81")
    # print(Result.success_response(ds)._get_data_for_json())




