# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12


import copy
from model_config import ModelConfig
from app.main.steel_factory.entity.stock import Stock
import pandas as pd
from app.util.db_pool import db_pool_db_sys
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
    data_path = get_path("5月6日库存明细.xls")
    df_stock1 = pd.read_excel(data_path)
    return df_stock1
    # sql_old = """
    #     SELECT
    #         stock_id as id,
    #         NOTICENUM as '发货通知单',
    #         order_no as '订单号',
    #         prior_flag as '优先发运',
    #         consignee_name as '收货用户',
    #         product_name as '品名名称',
    #         material_no as '牌号',
    #         spec_desc as '规格',
    #         DELIWAREHOUSE as '出库仓库',
    #         province_name as '省份',
    #         city_name as '城市',
    #         end_point_name as '终点',
    #         logistics_type as '物流公司类型',
    #         PACK as '包装形式',
    #         DETAILADDRESS as '卸货地址',
    #         new_pending_time as '最新挂单时间',
    #         DEVPERIOD as '合同约定交货日期',
    #         DELIWARE as '入库仓库'
    #     FROM
    #         db_dev.ods_outer_rgsd_warehouse_amount_20200509
    # """
    # sql_new = """
    #     SELECT
    #         stock_id as id,
    #         product_name as '品名',
    #         actual_number as '实际可发件数',
    #         Actual_weight as '实际可发重量',
    #         piece_weight as '件重'
    #     FROM
    #         db_dev.dwd_rgsd_warehouse_amount_20200509
    # """
    # df_old = pd.read_sql(sql_old, db_pool_ods.connection())
    # df_new = pd.read_sql(sql_new, db_pool_ods.connection())
    # df_result = pd.merge(df_old, df_new, on="id", how="right")
    # return df_result


def address_latitude_and_longitude():
    """获取数据表中地址经纬度信息

    Args:

    Returns:

    Raise:

    """
    sql1 = """
            select address as '卸货地址',longitude, latitude
            from t_point
        """
    sql2 = """
            select address as '卸货地址2',longitude, latitude 
            from t_point
            where longitude is not null
            And latitude is not null
            GROUP BY longitude, latitude
        """
    result_1 = pd.read_sql(sql1, db_pool_db_sys.connection())
    result_2 = pd.read_sql(sql2, db_pool_db_sys.connection())
    return result_1, result_2


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
    data1, data2 = address_latitude_and_longitude()
    # 存放stock的结果
    stock_list = []
    # 存放dataframe的结果
    result = pd.DataFrame()
    # 获取库存
    df_stock = get_stock()
    df_stock = pd.merge(df_stock, data1, on="卸货地址", how="left")
    df_stock = pd.merge(df_stock, data2, on=["latitude", "longitude"], how="left")
    df_stock["实际终点"] = df_stock["终点"]
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
    df_stock.loc[(df_stock["品名"] == "开平板") & (df_stock["出库仓库"].str.startswith("P") == False), ["品名"]] = ["开平板"]
    # stock2 = df_stock.loc[(df_stock["实际可发件数"] <= 0)]
    # print("筛选值:{}".format(stock2["实际可发重量"].sum()))
    # 筛选出不为0的数据
    df_stock = df_stock.loc[(df_stock["实际可发重量"] > 0) & (df_stock["实际可发件数"] > 0) & (df_stock["最新挂单时间"].notnull())]
    df_stock.loc[df_stock["入库仓库"].str.startswith("U"), ["实际终点"]] = df_stock["入库仓库"]
    df_stock.loc[df_stock["入库仓库"].str.startswith("U"), ["卸货地址2"]] = df_stock["港口批号"]
    df_stock.loc[df_stock["优先发运"].isnull(), ["优先发运"]] = ""
    result = result.append(df_stock)
    result = rename_pd(result)
    result.loc[result["Standard_address"].isnull(), ["Standard_address"]] = result["Address"]
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
        if not stock.Standard_address:
            stock.Standard_address = stock.Address
        if stock.Priority == "客户催货":
            stock.Priority = ModelConfig.RG_PRIORITY[stock.Priority]
        else:
            # if datetime.datetime.strptime(str(stock.Latest_order_time).split(".")[0], "%Y-%m-%d %H:%M:%S") <= (
            #         datetime.datetime.now() + datetime.timedelta(days=-2)):
            #     stock.Priority = "超期清理"
            # if datetime.datetime.strptime(str(stock.Delivery_date), "%Y%m%d") <= (datetime.datetime.now()):
            #     stock.Priority = "合同逾期"
            if stock.Priority:
                stock.Priority = ModelConfig.RG_PRIORITY[stock.Priority]
            else:
                stock.Priority = 4
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
                         "卸货地址2": "Standard_address",
                         "实际终点": "Actual_end_point"

                     },
                     inplace=True)
    return dataframe


if __name__ == "__main__":
    a = deal_stock()
    for i in a:
        print(i.Stock_id, i.Priority, i.Latest_order_time, i.Actual_weight, i.Piece_weight, i.Actual_number)
