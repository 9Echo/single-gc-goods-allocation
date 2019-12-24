# -*- coding: utf-8 -*-
# Description: 确认发货通知单
# Created: shaoluyu 2019/11/13
from app.main.entity.delivery_item import DeliveryItem
from app.utils.code import ResponseCode
from app.main.dao.delivery_log_dao import delivery_log_dao
from app.main.entity.delivery_log import DeliveryLog
from app.main.entity.delivery_sheet import DeliverySheet
from app.main.services.redis_service import get_delivery_list
from app.utils.my_exception import MyException


def generate_delivery(delivery_data):
    """
    根据json数据生成对应的发货通知单
    """
    delivery_item_list = []
    # for delivery in delivery_data:
    #     delivery_model = DeliverySheet(delivery)
    #     delivery_model.items = []

    for item in delivery_data['items']:
        delivery_item_model = DeliveryItem(item)
        delivery_item_list.append(delivery_item_model)

    return delivery_item_list


# def confirm(delivery):
#     """
#         确认发货通知单，获取Redis库存
#         :return:
#         """
#     try:
#         redis_conn = redis.Redis(connection_pool=redis_pool)
#         lock_id = RedisLock.try_lock(redis_conn, 'stock_lock', wait_time=20)
#         # 拿到锁，获取库存
#         if lock_id:
#             json_stock_list = redis_conn.get('gc:stocks')
#             if json_stock_list:
#                 stock_list = json.loads(json_stock_list)
#                 # 进行库存更新，库存不足不做更新
#                 result = subtract_stock(delivery, stock_list)
#                 # 如果扣减库存成功，重置Redis
#                 if result.code == ResponseCode.Info:
#                     json_data = json.dumps(result.data)
#                     redis_conn.set('gc:stocks', json_data)
#                     result.data = None
#                 return result
#
#         else:
#             return Result.error("销售太火爆了，请重试")
#
#     except Exception as e:
#         current_app.logger.info("confirm error")
#         current_app.logger.exception(e)
#     finally:
#         RedisLock.unlock(redis_conn, 'stock_lock', lock_id)
#         redis_conn.close()
#
#
# def subtract_stock(delivery, stock_list):
#     """
#     根据确认后的发货通知单，扣减库存
#     :return:
#     """
#     try:
#         msg = ""
#         tag = True
#         for i in delivery.items:
#             # 过滤出发货通知单指定的品种、规格、仓库、库位的库存数据，会出现有多条数据的情况
#             data_list = list(filter(lambda s: s['cname'] == i.product_type
#                                               and s['itemid'] == i.spec
#                                               and s['whsDesc'] == i.warehouse
#                                               and s['locid'] == str(i.loc_id), stock_list))
#
#             # 更新stock_list
#             stock_list = list(filter(lambda s: s['cname'] != i.product_type
#                                               or s['itemid'] != i.spec
#                                               or s['whsDesc'] != i.warehouse
#                                               or s['locid'] != str(i.loc_id), stock_list))
#             # 如果没有数据，也允许开单，并做出提示
#             if len(data_list) == 0:
#                 msg += "品名：" + i.product_type + "规格：" + i.spec + "没有库存  "
#                 # 管厂逻辑：如果库存没有找到开单的规格，在库存表插入一条库存数据，只有预留库存信息
#                 tag = False
#                 continue
#             else:
#                 # 校验发货通知单件数、散根数
#                 i.quantity = i.quantity if i.quantity is not None else 0
#                 i.free_pcs = i.free_pcs if i.free_pcs is not None else 0
#                 # 转换库存量
#                 def transform(row):
#                     row['enterJ'] = int(row['enterJ']) if row['enterJ'] is not None else 0
#                     row['enterG'] = int(row['enterG']) if row['enterG'] is not None else 0
#                     return row
#                 df_data = pandas.DataFrame(data_list)
#                 df_data = df_data.apply(transform, axis=1)
#                 # 得出库存总件数和总散根数的Series
#                 series = df_data.sum()
#                 # 如果库存不足，也允许开单，但做出提示
#                 if int(series['enterJ']) < int(i.quantity) or int(series['enterG']) < int(i.free_pcs):
#                     msg += "品名" + i.product_type + " 规格" + i.spec + " 库存不足，件数剩余"\
#                                     +series['enterJ'] +"件，散根剩余：" + series['enterG'] +"根   "
#                 # 得出剩余件数和散根数
#                 enter_j = int(series['enterJ']) - int(i.quantity)
#                 enter_g = int(series['enterG']) - int(i.free_pcs)
#                 # 创建一个新字典，更新库存
#                 new_dict = copy.deepcopy(data_list[0])
#                 new_dict['enterJ'] = str(enter_j)
#                 new_dict['enterG'] = str(enter_g)
#                 stock_list.append(new_dict)
#
#         if tag:
#             # 这里要改成更新发货通知单主子表,对比数据，将对比有差异的两条数据保存到log表，状态分别为初始状态、确认状态
#             # threading.Thread(target=delivery_sheet_dao.insert, args=(delivery,)).start()
#             # threading.Thread(target=delivery_item_dao.insert, args=(delivery.items,)).start()
#             return Result.info(msg=msg if msg != "" else "成功", data=stock_list)
#         else:
#             return Result.warn(msg)
#
#     except Exception as e:
#         current_app.logger.info("subtract stock error")
#         current_app.logger.exception(e)


def confirm(company_id, new_delivery_list):
    """
    将新数据删除、添加、更新的项写入log表
    :param: delivery是传过来的发货通知单对象列表
    :return:发货通知单对象列表
    """
    # 判断批次号的存在
    if not getattr(new_delivery_list[0], 'batch_no', None):
        raise MyException('批次号为空！', ResponseCode.Error)
    result_data = get_delivery_list(new_delivery_list[0].batch_no)
    # 如果没获取到原数据，结束操作
    if not getattr(result_data, 'data', None):
        return
    # 原明细数据
    old_item_list = result_data.data
    # 新明细数据
    new_item_list = []
    # 插入列表
    insert_list = list(filter(lambda i: not i.delivery_item_no, new_item_list))
    # 删除列表
    delete_list = list(
        filter(lambda i: i.delivery_item_no not in [j.delivery_item_no for j in new_item_list], old_item_list))
    # 更新列表
    new_update_list = list(
        filter(lambda i: i.delivery_item_no in [j.delivery_item_no for j in old_item_list], new_item_list))
    old_update_list = list(
        filter(lambda i: i.delivery_item_no in [j.delivery_item_no for j in new_item_list], old_item_list))
    # 合并列表
    log_list = merge(insert_list, delete_list, new_update_list, old_update_list, company_id)
    # 数据库操作
    delivery_log_dao.insert(log_list)
    return True


def merge(insert_list, delete_list, new_update_list, old_update_list, company_id):
    """
    合并列表，并做更新前后的对比
    :param insert_list:
    :param delete_list:
    :param new_update_list:
    :param old_update_list:
    :param company_id:
    :return:
    """
    # update状态
    log_update_list = []
    for i in old_update_list:
        for j in new_update_list:
            if i.delivery_item_no == j.delivery_item_no:
                if i.quantity != j.quantity or i.free_pcs != j.free_pcs:
                    log_update_list.append(
                        DeliveryLog(
                            {"company_id":company_id, "delivery_no": i.delivery_no, "delivery_item_no": i.delivery_item_no, "op": 2,
                             "quantity_before": i.quantity, "quantity_after": j.quantity,
                             "free_pcs_before": i.free_pcs,
                             "free_pcs_after": j.free_pcs}))
    # insert状态
    log_insert_list = [
        DeliveryLog({"company_id":company_id, "delivery_no": i.delivery_no, "delivery_item_no": i.delivery_item_no, "op": 1,
                     "quantity_before": 0, "quantity_after": i.quantity, "free_pcs_before": 0,
                     "free_pcs_after": i.free_pcs}) for i in insert_list]
    # delete状态
    log_delete_list = [
        DeliveryLog({"company_id":company_id, "delivery_no": i.delivery_no, "delivery_item_no": i.delivery_item_no, "op": 0,
                     "quantity_before": i.quantity, "quantity_after": 0,
                     "free_pcs_before": i.free_pcs,
                     "free_pcs_after": 0}) for i in delete_list]
    # 合并
    log_list = log_delete_list + log_insert_list + log_update_list
    return log_list


#
# if __name__ == '__main__':
#     basedir = os.path.realpath(os.path.dirname(__file__))
#     json_path = os.path.join(basedir, "..", "..", "analysis", "analysis", "delivery.json")
#     with open(json_path, 'r',encoding='UTF-8') as f:
#         delivery_data = json.loads(f.read())
#     # 创建发货通知单实例，初化属性
#     delivery_list = []
#     # for data in delivery_data['data']:
#     #     delivery_list.append(generate_delivery(data))
#     delivery_list=generate_delivery(delivery_data['data'])
#     print('start_time: ', time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))
#     confirm(delivery_list)
#     print('end_time: ', time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))
#     # ds = delivery_sheet_dao.get_one("ds_70247e800ce711ea9e81")
#     # print(Result.success_response(ds)._get_data_for_json())





