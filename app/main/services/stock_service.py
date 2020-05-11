# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12


import copy
import os
import datetime

from app.main.entity.stock import Stock
import pandas as pd
from app.main.db_pool import db_pool_db_sys
from app.utils.get_static_path import get_path


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
    # # 获取库存
    # datas = select_stock()
    # # 存放库存信息
    # stock_list = []
    # for data in datas:
    #     stock = Stock(data)
    #     stock_list.append(stock)
    # return stock_list
    data_path = get_path('sheet1.xls')
    df_stock1 = pd.read_excel(data_path, 1)
    df_stock3 = pd.read_excel(data_path, 4)
    return pd.concat([df_stock1, df_stock3], ignore_index=True)


def deal_stock():
    """

    :return:
    """
    """
        步骤：
        1 调用get_stock(),获取库存列表
        2 将可发重量+=需开单重量合并，可发件数+=需开单件数合并，
        若需短溢重量>0,减去相应的件数和重量，若品名为窄带，将可发件数=窄带捆包数,若品名为开平板，品名=if出库仓库包含P 西区开平板 else 老区开平板
        3 过滤掉可发重量或可发件数或窄带捆包数<=0的数据，过滤掉最新挂单时间为空的数据
        4 卸货地址标准化，由于存在差别在几个字左右的不同地址，但其实是一个地址的情况
        5 以33t为重量上限，将可发重量大于此值的库存明细进行拆分，拆分成重量<=33t的若干份
        6 得到新的库存列表，返回
        """
    sql = """
        select address as '卸货地址',longitude, latitude
        from t_point
    """
    sql1 = """
        select address as '卸货地址2',longitude, latitude 
        from t_point
        where longitude is not null
        And latitude is not null
        GROUP BY longitude, latitude
    """

    data = pd.read_sql(sql, db_pool_db_sys.connection())
    data2 = pd.read_sql(sql1, db_pool_db_sys.connection())
    # 存放stock的结果
    stock_list = []
    # 存放dataframe的结果
    result = pd.DataFrame()
    # 获取库存
    df_stock = get_stock()
    df_stock = pd.merge(df_stock, data, on="卸货地址", how="left")
    df_stock = pd.merge(df_stock, data2, on=["latitude", "longitude"], how="left")
    # 根据公式，计算实际可发重量，实际可发件数
    df_stock["实际可发重量"] = (df_stock["可发重量"] + df_stock["需开单重量"]) * 1000
    df_stock["实际可发件数"] = df_stock["可发件数"] + df_stock["需开单件数"]
    df_stock["需短溢重量"] = df_stock["需短溢重量"] * 1000
    # 窄带按捆包数计算，实际可发件数 = 捆包数
    df_stock.loc[df_stock["品名"] == "窄带", ["实际可发件数"]] = df_stock["窄带捆包数"]
    # 根据公式计算件重
    df_stock["件重"] = round(df_stock["实际可发重量"] / df_stock["实际可发件数"])
    df_stock["实际可发重量"] = df_stock["件重"] * df_stock["实际可发件数"]
    # print("分货前重量:{}".format(df_stock["实际可发重量"].sum()))
    # print("段以重量:{}".format(df_stock["需短溢重量"].sum()))
    # print("差值:{}".format(df_stock["实际可发重量"].sum() - df_stock["需短溢重量"].sum()))
    # 根据短溢的重量，扣除相应的实际可发件数和实际可发重量,此处math.ceil向上取出会报错，所以用的是另一种向上取整方法
    df_stock.loc[df_stock["需短溢重量"] > 0, ["实际可发件数"]] = df_stock["实际可发件数"] + (-df_stock["需短溢重量"] // df_stock["件重"])
    df_stock.loc[df_stock["需短溢重量"] > 0, ["实际可发重量"]] = df_stock["实际可发重量"] + df_stock["件重"] * (
                -df_stock["需短溢重量"] // df_stock["件重"])
    # print("除去短溢后:{}".format(df_stock["实际可发重量"].sum()))
    # 区分西老区的开平板
    df_stock.loc[(df_stock["品名"] == "开平板") & (df_stock["出库仓库"].str.startswith("P")), ["品名"]] = ["西区开平板"]
    df_stock.loc[(df_stock["品名"] == "开平板") & (df_stock["出库仓库"].str.startswith("P") == False), ["品名"]] = ["老区开平板"]
    # stock2 = df_stock.loc[(df_stock["实际可发件数"] <= 0)]
    # print("筛选值:{}".format(stock2["实际可发重量"].sum()))
    # 筛选出不为0的数据
    stock1 = df_stock.loc[(df_stock["实际可发重量"] > 0) & (df_stock["实际可发件数"] > 0) & (df_stock["最新挂单时间"].notnull())]
    result = result.append(stock1)
    result = rename_pd(result)
    result.loc[result["Address2"].isnull(), ["Address2"]] = result["Address"]
    # result.to_excel("3.xls")
    # print("分货之后总重量:{}".format(result["Actual_weight"].sum()))
    # return result
    dic = result.to_dict(orient="record")
    count_parent = 0
    for record in dic:
        count_parent += 1
        stock = Stock(record)
        stock.Parent_stock_id = count_parent
        stock.Actual_number = int(stock.Actual_number)
        stock.Actual_weight = int(stock.Actual_weight)
        stock.Piece_weight = int(stock.Piece_weight)
        if not stock.Address2:
            stock.Address2 = stock.Address
        if datetime.datetime.strptime(str(stock.Delivery_date), "%Y%m%d") <= (datetime.datetime.now() + datetime.timedelta(days=-2)):
            stock.Priority = "超期清理"
        # 使用数字代替优先级 0 表示最优先，以此类推
        if stock.Priority == "客户催货":
            stock.Priority = 0
        elif stock.Priority == "超期清理":
            stock.Priority = 1
        else:
            stock.Priority = 2
        # 按33000将货物分成若干份
        num = 33000 // stock.Piece_weight
        # 首先去除 件重大于33000的货物
        if num < 1:
            continue
        # 其次如果可装的件数大于实际可发件数，不用拆分，直接添加到stock_list列表中
        elif num > stock.Actual_number:
            stock_list.append(stock)
        # 最后不满足则拆分
        else:
            group_num = stock.Actual_number // num
            left_num = stock.Actual_number % num
            copy_1 = copy.deepcopy(stock)
            copy_1.Actual_number = int(left_num)
            copy_1.Actual_weight = left_num * stock.Piece_weight
            if left_num:
                stock_list.append(copy_1)
            for q in range(int(group_num)):
                copy_2 = copy.deepcopy(stock)
                copy_2.Actual_weight = num * stock.Piece_weight
                copy_2.Actual_number = int(num)
                stock_list.append(copy_2)
    # 按照优先发运和最新挂单时间排序
    stock_list.sort(key=lambda x: (x.Priority, x.Latest_order_time), reverse=False)
    count = 1
    # 为排序的stock对象赋Id
    for num in stock_list:
        num.Stock_id = count
        count += 1
    return stock_list


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
                         "发货通知单": "Delivery",
                         "订单号": "Order",
                         "优先发运": "Priority",
                         "收货用户": "Consumer",
                         "品名名称": "Small_product_name",
                         "品名": "Big_product_name",
                         "牌号": "mark",
                         "规格": "specs",
                         "出库仓库": "Warehouse_out",
                         "省份": "Province",
                         "城市": "City",
                         "终点": "End_point",
                         "物流公司类型": "Logistics",
                         "包装形式": "Pack_form",
                         "卸货地址": "Address",
                         "最新挂单时间": "Latest_order_time",
                         "合同约定交货日期": "Delivery_date",
                         "实际可发重量": "Actual_weight",
                         "实际可发件数": "Actual_number",
                         "件重": "Piece_weight",
                         "入库仓库": "Warehouse_in",
                         "卸货地址2": "Address2"

                     },
                     inplace=True)
    return dataframe


if __name__ == "__main__":
    a = deal_stock()
    # k = False
    # for i in a:
    #     if i.Delivery == "F2003310270" and i.Actual_weight > 30000:
    #         i.Actual_weight = 1
    #         for j in a:
    #             if j.Delivery == "F2003310270":
    #                 print(j.Actual_weight)
    #         k = True
    #     if k:
    #         break
    for i in a:
        print(i.Stock_id, i.Priority, i.Latest_order_time, i.Actual_weight, i.Piece_weight, i.Actual_number)
