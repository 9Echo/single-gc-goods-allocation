# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12
import copy
import datetime
import pandas as pd
from app.main.steel_factory.dao.out_stock_queue_dao import out_stock_queue_dao
from app.main.steel_factory.dao.single_stock_dao import stock_dao
from app.main.steel_factory.entity.load_task_item import LoadTaskItem
from app.main.steel_factory.entity.stock import Stock
from app.util.db_pool import db_pool_ods
from model_config import ModelConfig


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
    all_stock_list = stock_dao.select_stock()
    out_stock_list = out_stock_queue_dao.select_out_stock_queue()
    # 排队信息
    if out_stock_list:
        all_stock_list = [i for i in all_stock_list if
                          (i.get('deliware_house').split('-', 1)[0]) not in out_stock_list]
    target_stock_list = deal_stock(all_stock_list, truck)
    commodity_group = ModelConfig.RG_COMMODITY_GROUP[truck.big_commodity_name]
    # 根据目的地和可拼货品类筛选库存
    target_stock_list = [i for i in target_stock_list if
                         truck.dlv_spot_name_end == i.dlv_spot_name_end and commodity_group.__contains__(
                             i.big_commodity_name)]
    return target_stock_list


def deal_stock(all_stock_list, truck):
    # 获取库存列表
    df_stock = pd.DataFrame(all_stock_list)
    # 需与卸货的订单地址，数据库中保存的地址及经纬度合并
    df_stock = merge_stock(df_stock)
    df_stock["CANSENDWEIGHT"] = df_stock["CANSENDWEIGHT"].astype('float64')
    df_stock["CANSENDNUMBER"] = df_stock["CANSENDNUMBER"].astype('float64')
    df_stock["NEED_LADING_WT"] = df_stock["NEED_LADING_WT"].astype('float64')
    df_stock["NEED_LADING_NUM"] = df_stock["NEED_LADING_NUM"].astype('float64')
    df_stock["OVER_FLOW_WT"] = df_stock["OVER_FLOW_WT"].astype('float64')
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
    df_stock.loc[df_stock["OVER_FLOW_WT"] > 0, ["actual_weight"]] = df_stock["actual_weight"] + df_stock[
        "piece_weight"] * (
                                                                            -df_stock["OVER_FLOW_WT"] // df_stock[
                                                                        "piece_weight"])
    # 窄带按捆包数计算，实际可发件数 = 捆包数
    df_stock.loc[(df_stock["big_commodity_name"] == "窄带") & (df_stock["PACK_NUMBER"] > 0), ["actual_number"]] = \
        df_stock["PACK_NUMBER"]
    # 区分西老区
    df_stock.loc[
        (df_stock["big_commodity_name"] == "开平板") & (df_stock["deliware_house"].str.startswith("P")), [
            "big_commodity_name"]] = [
        "西区开平板"]
    df_stock.loc[(df_stock["big_commodity_name"] == "黑卷") & (df_stock["deliware_house"].str.startswith("P")), [
        "big_commodity_name"]] = ["西区黑卷"]
    df_stock.loc[
        (df_stock["big_commodity_name"] == "黑卷") & (df_stock["deliware_house"].str.startswith("P") is False), [
            "big_commodity_name"]] = ["老区黑卷"]
    # 筛选出大于0的数据
    df_stock = df_stock.loc[
        (df_stock["actual_weight"] > 0) & (df_stock["actual_number"] > 0) & (df_stock["latest_order_time"].notnull())]
    # 将终点统一赋值到实际终点，方便后续处理联运
    df_stock["actual_end_point"] = df_stock["dlv_spot_name_end"]
    df_stock.loc[df_stock["deliware"].str.startswith("U"), ["actual_end_point"]] = df_stock["deliware"]
    df_stock.loc[df_stock["deliware"].str.startswith("U"), ["standard_address"]] = df_stock["PORTNUM"]
    df_stock.loc[(df_stock["port_name_end"].isin(ModelConfig.RG_PORT_NAME_END_LYG)) & (
        df_stock["big_commodity_name"].isin(ModelConfig.RG_COMMODITY_LYG)), ["actual_end_point"]] = "U288-岚北港口库2LYG"
    # 按车辆流向筛选
    if truck.actual_end_point:
        df_stock = df_stock.loc[df_stock['actual_end_point'].isin(truck.actual_end_point)]
    # df_stock.loc[df_stock["优先发运"].isnull(), ["优先发运"]] = ""
    df_stock.loc[df_stock["standard_address"].isnull(), ["standard_address"]] = df_stock["detail_address"]
    dic = df_stock.to_dict(orient="record")
    # 存放stock的结果
    stock_list = []
    for record in dic:
        stock = Stock(record)
        stock.parent_stock_id = get_stock_id(stock)
        stock.actual_number = int(stock.actual_number)
        stock.actual_weight = int(stock.actual_weight)
        stock.piece_weight = int(stock.piece_weight)
        if not stock.standard_address:
            stock.standard_address = stock.detail_address
        if stock.priority == "客户催货":
            stock.priority = ModelConfig.RG_PRIORITY[stock.priority]
        else:
            if datetime.datetime.strptime(str(stock.latest_order_time), "%Y%m%d%H%M%S") <= (
                    datetime.datetime.now() + datetime.timedelta(days=-2)):
                stock.priority = "超期清理"
            if stock.priority:
                stock.priority = ModelConfig.RG_PRIORITY[stock.priority]
            else:
                stock.priority = 3
        # 按33000将货物分成若干份
        num = truck.load_weight // stock.piece_weight
        # 首先去除 件重大于33000的货物
        if num < 1:
            continue
        # 其次如果可装的件数大于实际可发件数，不用拆分，直接添加到stock_list列表中
        elif num > stock.actual_number:
            stock_list.append(stock)
        # 最后不满足则拆分
        else:
            group_num = stock.actual_number // num
            left_num = stock.actual_number % num
            copy_1 = copy.deepcopy(stock)
            copy_1.actual_number = int(left_num)
            copy_1.actual_weight = left_num * stock.piece_weight
            if left_num:
                stock_list.append(copy_1)
            for q in range(int(group_num)):
                copy_2 = copy.deepcopy(stock)
                copy_2.actual_weight = num * stock.piece_weight
                copy_2.actual_number = int(num)
                stock_list.append(copy_2)
    # 按照优先发运和最新挂单时间排序
    stock_list.sort(key=lambda x: (x.priority, x.latest_order_time), reverse=False)
    return stock_list


def address_latitude_and_longitude():
    """获取数据表中地址经纬度信息
    """
    sql1 = """
            select address as detail_address,longitude, latitude
            from ods_db_sys_t_point
        """
    sql2 = """
            select address as standard_address,longitude, latitude 
            from ods_db_sys_t_point
            where longitude is not null
            And latitude is not null
            GROUP BY longitude, latitude
        """
    result_1 = pd.read_sql(sql1, db_pool_ods.connection())
    result_2 = pd.read_sql(sql2, db_pool_ods.connection())
    return result_1, result_2


def merge_stock(df_stock):
    # data1,data2分别是需卸货的订单地址，数据库中保存的地址及经纬度
    data1, data2 = address_latitude_and_longitude()
    df_stock = pd.merge(df_stock, data1, on="detail_address", how="left")
    df_stock = pd.merge(df_stock, data2, on=["latitude", "longitude"], how="left")
    return df_stock