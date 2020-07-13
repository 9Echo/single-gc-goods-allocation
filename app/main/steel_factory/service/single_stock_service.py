# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12
import copy
import datetime
import pandas as pd
from app.main.steel_factory.dao.loading_detail_dao import loading_detail_dao
from app.main.steel_factory.dao.out_stock_queue_dao import out_stock_queue_dao
from app.main.steel_factory.dao.single_stock_dao import stock_dao
from app.main.steel_factory.entity.load_task_item import LoadTaskItem
from app.main.steel_factory.entity.stock import Stock
from app.util.get_weight_limit import get_lower_limit
from model_config import ModelConfig

flag = False


def get_stock_id(obj):
    """
    根据库存信息生成每条库存的唯一id
    """
    if isinstance(obj, Stock):
        return hash(obj.notice_num + obj.oritem_num + obj.deliware_house)
    elif isinstance(obj, LoadTaskItem):
        return hash(obj.notice_num + obj.oritem_num + obj.outstock_code)


def get_stock(truck):
    """
    根据车辆目的地和可运货物返回库存列表
    """
    # 根据品种查询库存
    all_stock_list = stock_dao.select_stock(truck)
    if not all_stock_list:
        return []
    # 查询各仓库排队信息：结果为字典{‘仓库号’：排队车数量}
    out_stock_dict = out_stock_queue_dao.select_out_stock_queue()
    # 按仓库号升序排序：结果为元组列表
    out_stock_dict = [(k, out_stock_dict[k]) for k in sorted(out_stock_dict.keys())]
    out_stock_list = list()
    if out_stock_dict:
        j = 0  # 元组列表out_stock_dict的索引
        for i in ModelConfig.WAREHOUSE_WAIT_DICT.keys():
            if out_stock_dict[j][1] > ModelConfig.WAREHOUSE_WAIT_DICT[i]:
                out_stock_list.append(i)
            j += 1
    # 去除等待数较高的出库仓库，暂不往该仓库开单
    if out_stock_list:
        all_stock_list = [i for i in all_stock_list if i.get('deliware_house') not in out_stock_list]
    # 获取已开装车清单信息、预装车清单信息、最大更新时间、开单推荐但未经过确认
    loading_detail_list = loading_detail_dao.select_loading_detail(truck)
    # 扣除操作
    for stock_dict in all_stock_list:
        # 找出库存中被开单的子项
        temp_list = [j for j in loading_detail_list if j.get('notice_num') == stock_dict.get('notice_num') and j.get(
            'oritem_num') == stock_dict.get('oritem_num') and j.get('outstock_name') == stock_dict.get(
            'deliware_house')]
        if temp_list:
            for i in temp_list:
                stock_dict['CANSENDWEIGHT'] = float(stock_dict.get('CANSENDWEIGHT', 0)) - float(i.get('weight', 0))
                stock_dict['CANSENDNUMBER'] = int(stock_dict.get('CANSENDNUMBER', 0)) - int(i.get('count', 0))
    if not all_stock_list:
        return []
    # 库存预处理
    target_stock_list = deal_stock(all_stock_list, truck)
    return target_stock_list


def deal_stock(all_stock_list, truck):
    # 获取库存列表
    df_stock = pd.DataFrame(all_stock_list)
    # 需与卸货的订单地址，数据库中保存的地址及经纬度合并
    # df_stock = merge_stock(df_stock)
    df_stock["CANSENDWEIGHT"] = df_stock["CANSENDWEIGHT"].astype('float64')
    df_stock["CANSENDNUMBER"] = df_stock["CANSENDNUMBER"].astype('int64')
    df_stock["NEED_LADING_WT"] = df_stock["NEED_LADING_WT"].astype('float64')
    df_stock["NEED_LADING_NUM"] = df_stock["NEED_LADING_NUM"].astype('int64')
    df_stock["OVER_FLOW_WT"] = df_stock["OVER_FLOW_WT"].astype('float64')
    df_stock["waint_fordel_number"] = df_stock["waint_fordel_number"].astype('int64')
    df_stock["waint_fordel_weight"] = df_stock["waint_fordel_weight"].astype('float64')
    # 根据公式，计算实际可发重量，实际可发件数
    df_stock["actual_weight"] = (df_stock["CANSENDWEIGHT"] + df_stock["NEED_LADING_WT"]) * 1000
    df_stock["actual_number"] = df_stock["CANSENDNUMBER"] + df_stock["NEED_LADING_NUM"]
    # 根据公式计算件重
    df_stock["piece_weight"] = round(df_stock["actual_weight"] / df_stock["actual_number"])
    df_stock["actual_weight"] = df_stock["piece_weight"] * df_stock["actual_number"]
    # 需短溢处理
    df_stock["OVER_FLOW_WT"] = df_stock["OVER_FLOW_WT"] * 1000
    df_stock.loc[df_stock["OVER_FLOW_WT"] > 0, ["actual_number"]] = df_stock["actual_number"] + (
            -df_stock["OVER_FLOW_WT"] // df_stock["piece_weight"])
    # 筛选出大于0的数据
    df_stock = df_stock.loc[
        (df_stock["actual_weight"] > 0) & (df_stock["actual_number"] > 0) & (
            df_stock["latest_order_time"].notnull())]
    if df_stock.empty:
        return []
    global flag
    flag = False

    def rename(row):
        global flag
        if not flag:
            flag = True
            return row
        # 将所有黑卷置成卷板
        if row['big_commodity_name'] == '黑卷':
            row['big_commodity_name'] = '卷板'
        # 如果是西区开平板，则改为新产品-冷板
        if row['deliware_house'].startswith("P") and row['big_commodity_name'] == '开平板':
            row['big_commodity_name'] = '新产品-冷板'
        # 如果是西区非开平板，则品名前加新产品-
        elif row['deliware_house'].startswith("P") and row['big_commodity_name'] != '开平板':
            row['big_commodity_name'] = '新产品-' + row['big_commodity_name']
        # 如果是外库，且是西区品种，则品名前加新产品-
        elif (row['deliware_house'].find('F10') != -1 or row['deliware_house'].find('F20') != -1) and row[
            'big_commodity_name'] in ['白卷', '窄带', '冷板']:
            row['big_commodity_name'] = '新产品-' + row['big_commodity_name']
        # 其余全部是老区-
        else:
            row['big_commodity_name'] = '老区-' + row['big_commodity_name']
        return row

    df_stock = df_stock.apply(rename, axis=1)
    # 窄带按捆包数计算，实际可发件数 = 捆包数
    df_stock.loc[(df_stock["big_commodity_name"] == "新产品-窄带") & (df_stock["PACK_NUMBER"] > 0), ["actual_number"]] = \
        df_stock["PACK_NUMBER"]
    # 将终点统一赋值到实际终点，方便后续处理联运
    df_stock["actual_end_point"] = df_stock["dlv_spot_name_end"]
    df_stock.loc[df_stock["deliware"].str.startswith("U"), ["actual_end_point"]] = df_stock["deliware"]
    df_stock.loc[df_stock["deliware"].str.startswith("U"), ["standard_address"]] = df_stock["PORTNUM"]
    df_stock.loc[(df_stock["port_name_end"].isin(ModelConfig.RG_PORT_NAME_END_LYG)) & (
        df_stock["big_commodity_name"].isin(ModelConfig.RG_COMMODITY_LYG)), ["actual_end_point"]] = "U288-岚北港口库2LYG"
    # 按车辆流向筛选
    if truck.actual_end_point:
        df_stock = df_stock.loc[df_stock['actual_end_point'].isin(truck.actual_end_point)]
    df_stock.loc[df_stock["standard_address"].isnull(), ["standard_address"]] = df_stock["detail_address"]
    dic = df_stock.to_dict(orient="record")
    # 存放stock的结果
    stock_list = []
    for record in dic:
        stock = Stock(record)
        # 如果可发小于待发，并且待发在标载范围内，就不参与配载
        if stock.actual_number < stock.waint_fordel_number and get_lower_limit(stock.big_commodity_name) <= \
                stock.waint_fordel_weight <= ModelConfig.RG_MAX_WEIGHT:
            continue
        stock.parent_stock_id = get_stock_id(stock)
        stock.actual_number = int(stock.actual_number)
        stock.actual_weight = int(stock.actual_weight)
        stock.piece_weight = int(stock.piece_weight)
        stock.priority = ModelConfig.RG_PRIORITY.get(stock.priority, 4)
        if datetime.datetime.strptime(str(stock.latest_order_time), "%Y%m%d%H%M%S") <= (
                datetime.datetime.now() + datetime.timedelta(days=-2)):
            stock.priority = ModelConfig.RG_PRIORITY["超期清理"]
        # 组数
        target_group_num = 0
        # 临时组数
        temp_group_num = 0
        # 最后一组件数
        target_left_num = 0
        # 一组几件
        target_num = 0
        for weight in range(get_lower_limit(stock.big_commodity_name), ModelConfig.RG_MAX_WEIGHT + 1000, 1000):
            # 一组几件
            num = weight // stock.piece_weight
            if num < 1 or num > stock.actual_number or (num * stock.piece_weight) < get_lower_limit(
                    stock.big_commodity_name):
                target_num = num
                continue
            # 组数
            group_num = stock.actual_number // num
            # 最后一组件数
            left_num = stock.actual_number % num
            # 如果最后一组符合标载条件，临时组数加1
            temp_num = 0
            if (left_num * stock.piece_weight) >= get_lower_limit(stock.big_commodity_name):
                temp_num = 1
            # 如果分的每组件数更多，并且组数不减少，就替换
            if (group_num + temp_num) >= temp_group_num:
                target_group_num = group_num
                temp_group_num = group_num + temp_num
                target_left_num = left_num
                target_num = num
        # 按33000将货物分成若干份
        # num = (truck.load_weight + ModelConfig.RG_SINGLE_UP_WEIGHT) // stock.piece_weight
        # 首先去除 件重大于33000的货物
        if target_num < 1:
            continue
        # 其次如果可装的件数大于实际可发件数，不用拆分，直接添加到stock_list列表中
        elif target_num > stock.actual_number:
            stock.limit_mark = 0
            stock_list.append(stock)
        # 最后不满足则拆分
        else:
            limit_mark = 1
            for q in range(int(target_group_num)):
                copy_2 = copy.deepcopy(stock)
                copy_2.actual_weight = target_num * stock.piece_weight
                copy_2.actual_number = int(target_num)
                if copy_2.actual_weight < get_lower_limit(stock.big_commodity_name):
                    limit_mark = 0
                else:
                    limit_mark = 1
                copy_2.limit_mark = limit_mark
                stock_list.append(copy_2)
            if target_left_num:
                copy_1 = copy.deepcopy(stock)
                copy_1.actual_number = int(target_left_num)
                copy_1.actual_weight = target_left_num * stock.piece_weight
                copy_1.limit_mark = limit_mark
                stock_list.append(copy_1)
    # 按照优先发运和最新挂单时间排序
    stock_list.sort(key=lambda x: (x.priority, x.latest_order_time, x.actual_weight * -1), reverse=False)
    return stock_list
