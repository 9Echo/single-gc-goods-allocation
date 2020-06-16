# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12
import copy

import pandas as pd

from app.main.steel_factory.entity.load_task_item import LoadTaskItem
from app.main.steel_factory.entity.stock import Stock
from app.main.steel_factory.service.dispatch_service import dispatch
from app.main.steel_factory.service.generate_excel_service import generate_excel
from app.main.steel_factory.service.truck_service import get_truck
from app.util.db_pool import db_pool_ods
from app.util.get_static_path import get_path
from model_config import ModelConfig

file_name = 'test_stock.xls'

def get_stock_id(obj):
    """
    根据库存信息生成每条库存的唯一id
    """
    if isinstance(obj, Stock):
        return hash(obj.notice_num + obj.oritem_num + obj.deliware_house)
    elif isinstance(obj, LoadTaskItem):
        return hash(obj.notice_num + obj.oritem_num + obj.outstock_code)


def get_all_stock():
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
    # 存放stock的结果
    stock_list = []
    # 存放dataframe的结果
    result = pd.DataFrame()
    # 获取库存
    data_path = get_path(file_name)
    df_stock = pd.read_excel(data_path)
    #与需卸货的订单地址，数据库中保存的地址及经纬度合并
    df_stock = merge_stock(df_stock)
    #数据预处理
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
    result.loc[result["standard_address"].isnull(), ["standard_address"]] = result["detail_address"]
    result.to_excel("3.xls")
    # print("分货之后总重量:{}".format(result["Actual_weight"].sum()))
    # return result
    dic = result.to_dict(orient="record")
    count_parent = 0
    for record in dic:
        count_parent += 1
        stock = Stock(record)
        stock.parent_stock_id = count_parent
        stock.actual_number = int(stock.actual_number)
        stock.actual_weight = int(stock.actual_weight)
        stock.piece_weight = int(stock.piece_weight)
        if not stock.standard_address:
            stock.standard_address = stock.detail_address
        if stock.priority == "客户催货":
            stock.priority = ModelConfig.RG_PRIORITY[stock.priority]
        else:
            # if datetime.datetime.strptime(str(stock.Latest_order_time).split(".")[0], "%Y-%m-%d %H:%M:%S") <= (
            #         datetime.datetime.now() + datetime.timedelta(days=-2)):
            #     stock.Priority = "超期清理"
            # if datetime.datetime.strptime(str(stock.Delivery_date), "%Y%m%d") <= (datetime.datetime.now()):
            #     stock.Priority = "合同逾期"
            if stock.priority:
                stock.priority = ModelConfig.RG_PRIORITY[stock.priority]
            else:
                stock.priority = 4
        # 按33000将货物分成若干份
        num = 33000 // stock.piece_weight
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
    count = 1
    # 为排序的stock对象赋Id
    for num in stock_list:
        num.stock_id = count
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
                         "发货通知单": "notice_num",
                         "订单号": "oritem_num",
                         "优先发运": "priority",
                         "收货用户": "consumer",
                         "品名名称": "commodity_name",
                         "品名": "big_product_name",
                         "牌号": "mark",
                         "规格": "specs",
                         "出库仓库": "deliware_house",
                         "省份": "province",
                         "城市": "city",
                         "终点": "dlv_spot_name_end",
                         "物流公司类型": "logistics_company_type",
                         "包装形式": "pack",
                         "卸货地址": "detail_address",
                         "最新挂单时间": "latest_order_time",
                         "合同约定交货日期": "devperiod",
                         "实际可发重量": "actual_weight",
                         "实际可发件数": "actual_number",
                         "件重": "piece_weight",
                         "入库仓库": "deliware",
                         "卸货地址2": "standard_address",
                         "实际终点": "actual_end_point"

                     },
                     inplace=True)
    return dataframe


def address_latitude_and_longitude():
    """获取数据表中地址经纬度信息
    """
    sql1 = """
            select address as '卸货地址',longitude, latitude
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


def merge_stock(df_stock):
    #data1,data2分别是需卸货的订单地址，数据库中保存的地址及经纬度
    data1, data2 = address_latitude_and_longitude()
    df_stock = pd.merge(df_stock, data1, on="卸货地址", how="left")
    df_stock = pd.merge(df_stock, data2, on=["latitude", "longitude"], how="left")
    return df_stock


if __name__ == '__main__':
    truck_list=get_truck("truck.xls")
    stock_list = get_stock(truck_list[0])

    print(stock_list[0].as_dict())
