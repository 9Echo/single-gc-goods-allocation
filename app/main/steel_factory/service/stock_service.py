# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12
import copy

from app.util.code import ResponseCode
from app.util.my_exception import MyException
from model_config import ModelConfig
from app.main.steel_factory.entity.stock import Stock
import pandas as pd
from app.util.db_pool import db_pool_ods
from app.util.get_static_path import get_path


def get_stock():
    """
    获取库存
    :param vehicle:
    :return: 库存
    """
    """
    步骤：
    1 读取Excel，省内1  0点库存明细和省内2、3及连云港库存两个sheet页
    2 数据合并
    """
    data_path = get_path("sheet1.xls")
    df_stock1 = pd.read_excel(data_path)
    return df_stock1


def address_latitude_and_longitude():
    """获取数据表中地址经纬度信息

    Args:

    Returns:

    Raise:

    """
    sql1 = """
            select address as 'detail_address',longitude, latitude
            from ods_db_sys_t_point
        """
    sql2 = """
            select address as '卸货地址2',longitude, latitude 
            from ods_db_sys_t_point
            where longitude is not null
            And latitude is not null
            GROUP BY longitude, latitude
        """
    result_1 = pd.read_sql(sql1, db_pool_ods.connection())
    result_2 = pd.read_sql(sql2, db_pool_ods.connection())
    return result_1, result_2


def deal_stock(data):
    """

    :return:
    """
    """
        步骤：
        1 调用get_stock(),获取库存列表
        2 可发重量+=需开单重量合并，可发件数+=需开单件数合并，
        若需短溢重量>0,减去相应的件数和重量，若品名为窄带，将可发件数=窄带捆包数,若品名为开平板，品名=if出库仓库包含P 西区开平板 else 老区开平板
        3 过滤掉可发重量或可发件数或窄带捆包数<=0的数据，过滤掉最新挂单时间为空的数据
        4 卸货地址标准化，由于存在差别在几个字左右的不同地址，但其实是一个地址的情况
        5 以33t为重量上限，将可发重量大于此值的库存明细进行拆分，拆分成重量<=33t的若干份
        6 得到新的库存列表，返回
        """
    if not data:
        raise MyException('输入列表为空', ResponseCode.Error)
    data1, data2 = address_latitude_and_longitude()
    # 存放满足条件的stock结果
    stock_list = []
    # 存放筛除的stock结果
    sift_stock_list = []
    # 存放dataframe的结果
    result = pd.DataFrame()
    # 获取库存
    df_stock = pd.DataFrame(data)
    # df_stock = get_stock()
    # ——————————————注释开始
    df_stock = pd.merge(df_stock, data1, on="detail_address", how="left")
    df_stock = pd.merge(df_stock, data2, on=["latitude", "longitude"], how="left")
    df_stock["实际终点"] = df_stock["dlv_spot_name_end"]
    # 根据公式，计算实际可发重量，实际可发件数
    # df_stock["实际可发重量"] = (df_stock["can_send_weight"] + df_stock["need_lading_wt"]) * 1000
    df_stock["实际可发重量"] = df_stock["can_send_weight"] * 1000
    # df_stock["实际可发件数"] = df_stock["can_send_number"] + df_stock["need_lading_num"]
    df_stock["实际可发件数"] = df_stock["can_send_number"]
    # df_stock["over_flow_wt"] = df_stock["over_flow_wt"] * 1000
    # 窄带按捆包数计算，实际可发件数 = 捆包数
    # df_stock.loc[(df_stock["big_commodity_name"] == "窄带") & (df_stock["pack_number"] > 0), ["实际可发件数"]] = df_stock[
    #     "pack_number"]
    # # 根据公式计算件重
    df_stock["件重"] = round(df_stock["实际可发重量"] / df_stock["实际可发件数"])
    df_stock["实际可发重量"] = df_stock["件重"] * df_stock["实际可发件数"]
    # print("分货前重量:{}".format(df_stock["实际可发重量"].sum()))
    # print("段以重量:{}".format(df_stock["需短溢重量"].sum()))
    # print("差值:{}".format(df_stock["实际可发重量"].sum() - df_stock["需短溢重量"].sum()))
    # 根据短溢的重量，扣除相应的实际可发件数和实际可发重量,此处math.ceil向上取出会报错，所以用的是另一种向上取整方法
    # df_stock.loc[df_stock["over_flow_wt"] > 0, ["实际可发件数"]] = df_stock["实际可发件数"] + (
    #             -df_stock["over_flow_wt"] // df_stock["件重"])
    # df_stock.loc[df_stock["over_flow_wt"] > 0, ["实际可发重量"]] = df_stock["实际可发重量"] + df_stock["件重"] * (
    #         -df_stock["over_flow_wt"] // df_stock["件重"])
    # print("除去短溢后:{}".format(df_stock["实际可发重量"].sum()))
    # 区分西老区的开平板
    df_stock.loc[(df_stock["big_commodity_name"] == "开平板") & (df_stock["deliware_house"].str.startswith("P")), [
        "big_commodity_name"]] = ["西区开平板"]
    # df_stock.loc[
    #     (df_stock["big_commodity_name"] == "开平板") & (df_stock["deliware_house"].str.startswith("P") is False), [
    #         "big_commodity_name"]] = ["开平板"]
    df_stock.loc[(df_stock["big_commodity_name"] == "黑卷") & (df_stock["deliware_house"].str.startswith("P")), [
        "big_commodity_name"]] = ["西区黑卷"]
    df_stock.loc[
        (df_stock["big_commodity_name"] == "黑卷") & (df_stock["deliware_house"].str.startswith("P") is False), [
            "big_commodity_name"]] = ["老区黑卷"]
    # stock2 = df_stock.loc[(df_stock["实际可发件数"] <= 0)]
    # print("筛选值:{}".format(stock2["实际可发重量"].sum()))
    # 筛选出不为0的数据
    df_stock_temp = df_stock.loc[
        (df_stock["实际可发重量"] > 0) & (df_stock["实际可发件数"] > 0) & (df_stock["latest_order_time"].notnull())]
    # 可发件数小于待发件数并且待发重量在31-33，则过滤掉
    df_stock_temp.drop(
        index=(df_stock_temp.loc[
                   (df_stock_temp["can_send_number"] < df_stock_temp["waint_fordel_number"]) & (
                           31 <= df_stock_temp["waint_fordel_weight"]) & (
                           df_stock_temp["waint_fordel_weight"] <= 33)].index),
        inplace=True)

    df_stock_temp.loc[df_stock_temp["deliware"].str.startswith("U"), ["实际终点"]] = df_stock_temp["deliware"]
    df_stock_temp.loc[(df_stock_temp["port_name_end"].isin(ModelConfig.RG_PORT_NAME_END_LYG)) & (
        df_stock_temp["big_commodity_name"].isin(ModelConfig.RG_COMMODITY_LYG)), ["实际终点"]] = "U288-岚北港口库2LYG"
    df_stock_temp.loc[df_stock_temp["deliware"].str.startswith("U"), ["卸货地址2"]] = df_stock_temp["portnum"]
    df_stock_temp.loc[df_stock_temp["priority"].isnull(), ["priority"]] = ""
    df_stock_temp["sort"] = 3
    df_stock_temp.loc[
        (df_stock_temp["实际可发重量"] <= ModelConfig.RG_MAX_WEIGHT) & (
                df_stock_temp["实际可发重量"] >= ModelConfig.RG_MIN_WEIGHT), [
            "sort"]] = 2
    # ——————————————注释结束
    # 找出被筛除的项
    df_stock = df_stock.append(df_stock_temp)
    df_stock = df_stock.drop_duplicates(keep=False)
    df_stock["sift_away"] = True
    df_stock_temp = df_stock_temp.append(df_stock)
    result = result.append(df_stock_temp)
    result = rename_pd(result)
    # 如果标准地址没有匹配到，那么就是用详细地址代替
    result.loc[result["standard_address"].isnull(), ["standard_address"]] = result["detail_address"]
    # print("分货之后总重量:{}".format(result["actual_weight"].sum()))
    dic = result.to_dict(orient="record")
    count_parent = 0
    for record in dic:

        count_parent += 1
        stock = Stock(record)
        if stock.sift_away:
            sift_stock_list.append(stock)
            continue
        stock.parent_stock_id = count_parent
        stock.actual_number = int(stock.actual_number)
        stock.actual_weight = int(stock.actual_weight)
        stock.piece_weight = int(stock.piece_weight)
        if not stock.standard_address:
            stock.standard_address = stock.detail_address
        if stock.priority == "客户催货":
            stock.priority = ModelConfig.RG_PRIORITY[stock.priority]
        else:
            # if datetime.datetime.strptime(str(stock.latest_order_time).split(".")[0], "%Y-%m-%d %H:%M:%S") <= (
            #         datetime.datetime.now() + datetime.timedelta(days=-2)):
            #     stock.priority = "超期清理"
            if stock.priority in ModelConfig.RG_PRIORITY:
                stock.priority = ModelConfig.RG_PRIORITY[stock.priority]
            else:
                stock.priority = 3
        if (stock.priority in ModelConfig.RG_PRIORITY.values()
                and ModelConfig.RG_SECOND_MIN_WEIGHT <= stock.piece_weight < ModelConfig.RG_MIN_WEIGHT):
            stock.sort = 1
        # 按33000将货物分成若干份
        num = ModelConfig.RG_MAX_WEIGHT // stock.piece_weight
        # 首先去除 件重大于33000的货物
        if num < 1:
            sift_stock_list.append(stock)
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
                if ModelConfig.RG_MIN_WEIGHT <= copy_1.actual_weight <= ModelConfig.RG_MAX_WEIGHT:
                    copy_1.sort = 2
                stock_list.append(copy_1)
            for q in range(int(group_num)):
                copy_2 = copy.deepcopy(stock)
                copy_2.actual_weight = num * stock.piece_weight
                copy_2.actual_number = int(num)
                if ModelConfig.RG_MIN_WEIGHT <= copy_2.actual_weight <= ModelConfig.RG_MAX_WEIGHT:
                    copy_2.sort = 2
                stock_list.append(copy_2)
    # 按照优先发运和最新挂单时间排序
    stock_list.sort(key=lambda x: (x.sort, x.priority, x.latest_order_time), reverse=False)
    count = 1
    # 为排序的stock对象赋Id
    for num in copy.copy(stock_list):
        num.stock_id = count
        count += 1
    if not stock_list:
        raise MyException('输入可发库存无效', ResponseCode.Error)
    return stock_list, sift_stock_list


def rename_pd(dataframe):
    """
    更改列名
    Args:
        dataframe: dataframe数据

    Returns:

    Raise:

    """
    dataframe.rename(index=str,
                     columns={
                         "material": "mark",
                         "standard": "specs",
                         "实际可发重量": "actual_weight",
                         "实际可发件数": "actual_number",
                         "件重": "piece_weight",
                         "卸货地址2": "standard_address",
                         "实际终点": "actual_end_point"
                     },
                     inplace=True)
    return dataframe


if __name__ == "__main__":
    a = deal_stock()
    # for i, j in b.items():
    #     for k in j:
    #         print(i, k.priority, k.actual_weight)
    # for i in a:
    #     print(i.sort, i.priority, i.latest_order_time)
    # if i.priority not in (1, 2, 3):
    #     print(i.stock_id, i.priority, i.latest_order_time, i.actual_weight, i.piece_weight, i.actual_number)
