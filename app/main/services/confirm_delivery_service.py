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
            deli_dic = delivery_sheet_dao.get_by_sheet(delivery.delivery_no)
            deli_item_list_dic = delivery_item_dao.get_by_sheet(delivery.delivery_no)
            print('deli_item_list_dic:  ', deli_item_list_dic)
            for i in delivery.items:
                flag = True
                for j in deli_item_list_dic:
                    pass
                    # print(i, i.delivery_item_no)
                    # print(j, j["delivery_item_no"])
                    # if i["delivery_item_no"] == j["delivery_item_no"] and (i["status"] != j["status"] or
                    # i["customer_id"] != j["customer_id"] or i["salesman_id"] != j["salesman_id"] or i["dest"] != j["dest"] or
                    # i["product_type"] != j["product_type"] or i["spec"] != j["spec"] or i["weight"] != j["weight"] or
                    # i["warehouse"] != j["warehouse"] or i["loc_id"] != j["loc_id"] or i["quantity"] != j["quantity"] or
                    # i["free_pcs"] != j["free_pcs"] or i["total_pcs"] != j["total_pcs"]):
                    #     flag = False

            if flag == False:
                pass
            delivery_sheet_dao.update(delivery)
            # delivery_item_dao.update(delivery.items)
            return Result.success(new_list)
        else:
            return Result.warn(msg)

    except Exception as e:
        current_app.logger.info("subtract stock error")
        current_app.logger.exception(e)
