# -*- coding: utf-8 -*-
# Description: 确认发货通知单
# Created: shaoluyu 2019/11/13
import copy
import json
import threading

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
                                              and s['locid'] == i.loc_id, stock_list))
            # 如果扣减库存成功最终返回的list
            new_list = list(filter(lambda s: s['cname'] != i.product_type
                                              and s['itemid'] != i.spec
                                              and s['whsDesc'] != i.warehouse
                                              and s['locid'] != i.loc_id, stock_list))
            # 如果没有数据
            if len(data_list) == 0:
                msg += "品名：" + i.product_type + "规格：" + i.spec + "没有库存  "
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
                # 如果库存不足
                if int(series['enterJ']) < int(i.quantity) or int(series['enterG']) < int(i.free_pcs):
                    msg += "品名：" + i.product_type + "规格：" + i.spec + "库存不足，件数剩余："\
                                    +series['enterJ'] +"件，散根剩余：" + series['enterG'] +"根   "
                    tag = False
                    continue
                # 得出剩余件数和散根数
                enter_j = int(series['enterJ']) - int(i.quantity)
                enter_g = int(series['enterG']) - int(i.free_pcs)
                # 创建一个新字典，更新库存
                new_dict = copy.deepcopy(data_list[0])
                new_dict['enterJ'] = str(enter_j)
                new_dict['enterG'] = str(enter_g)
                new_list.append(new_dict)

        if tag:
            # 这里要改成更新发货通知单主子表,对比数据，将对比有差异的两条数据保存到log表，状态分别为初始状态、确认状态
            # threading.Thread(target=delivery_sheet_dao.insert, args=(delivery,)).start()
            # threading.Thread(target=delivery_item_dao.insert, args=(delivery.items,)).start()
            return Result.success(new_list)
        else:
            return Result.warn(msg)

    except Exception as e:
        current_app.logger.info("subtract stock error")
        current_app.logger.exception(e)


def update_delviery_sheet(delivery):
    """更新数据库中发货通知单记录"""
    # origin = delivery_sheet_dao.get_by_order_id(delivery_sheet.order_id)
    # origin_items =

    #  新数据：delivery_sheet
    #  原数据

    origin_items = delivery_item_dao.get_one(delivery.delivery_no)

    log_insert_list = []  # log表数据
    total_quantity = 0    # 主表的总数量
    free_pcs = 0          # 主表的散根数
    update_list = []      # 更新子表的数据列表
    insert_list = []         # 添加子表的数据列表
    delete_list = []      # 删除子表的数据列表
    # 记录delivery_sheet中有，origin_items中也有的发货通知单号
    list_both = []
    for i in delivery.items:
        i = DeliveryItem(i)
        flag = False
        for j in origin_items:
            j = DeliveryItem(j)
            if i.delivery_item_no == j.delivery_item_no:
                # delivery_sheet中有origin_items对应的子表记录，log中记为更改：2
                list_both.append(i.delivery_item_no)
                flag = True
                if int(i.quantity) != int(j.quantity) or int(i.free_pcs) != int(j.free_pcs):
                    log_dic = {"delivery_no": i.delivery_no, "delivery_item_no": i.delivery_item_no, "op": '2',
                               "quantity_before": int(j.quantity), "quantity_after":int(i.quantity), "free_pcs_before":
                               int(j.free_pcs), "free_pcs_after": int(i.free_pcs)}
                    log = DeliveryLog(log_dic)
                    log_insert_list.append(log)
                    update_list.append(i)
        total_quantity += i.quantity
        free_pcs += i.free_pcs

        # origin_items中没有delivery_sheet对应的子表记录，log中记为添加：1
        if flag == False:
            log_dic = {"delivery_no": i.delivery_no, "delivery_item_no": i.delivery_item_no, "op": '1',
                       "quantity_before": 0, "quantity_after": int(i.quantity), "free_pcs_before": 0,
                       "free_pcs_after": int(i.free_pcs)}
            log = DeliveryLog(log_dic)
            log_insert_list.append(log)
            insert_list.append(i)
    # delivery_sheet中没有origin_items对应的子表记录，log中记为删除：0
    # print(list_both)
    for j in origin_items:
        j = DeliveryItem(j)
        if j.delivery_item_no not in list_both:
            log_dic = {"delivery_no": j.delivery_no, "delivery_item_no": j.delivery_item_no, "op": '0',
                       "quantity_before": int(j.quantity), "quantity_after": 0,
                       "free_pcs_before": int(j.free_pcs), "free_pcs_after": 0}
            log = DeliveryLog(log_dic)
            log_insert_list.append(log)
            delete_list.append(j)

    # 更新log表数据
    delivery_log_dao.insert(log_insert_list)
    # 更新主表数据
    delivery.total_quantity = total_quantity
    delivery.free_pcs = free_pcs
    delivery_sheet_dao.update(delivery)
    # 更改子表数据
    delivery_item_dao.update(update_list)
    delivery_item_dao.delete(delete_list)
    delivery_item_dao.insert(insert_list)


if __name__ == '__main__':
    basedir = os.path.realpath(os.path.dirname(__file__))
    json_path = os.path.join(basedir, "..", "..", "analysis", "analysis", "delivery.py")
    with open(json_path, 'r',encoding='UTF-8') as f:
        datas = json.loads(f.read())
    # 创建发货通知单实例，初始化属性
    delivery = DeliverySheet(datas["data"])
    update_delviery_sheet(delivery)
