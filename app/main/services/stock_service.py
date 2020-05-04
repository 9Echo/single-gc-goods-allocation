# -*- coding: utf-8 -*-
# Description: 库存服务
# Created: shaoluyu 2020/03/12

"""
库存管理局限：
1、库存来源是日钢中间库，每20分钟可获取最新库存，并且库存信息跟实际库存有误差
2、没有修改库存的权限
"""
from typing import List

from app.main.dao.stock_dao import select_stock
from app.main.entity.stock import Stock
import copy


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
    # 获取库存
    datas = select_stock()
    # 存放库存信息
    stock_list = []
    for data in datas:
        stock = Stock(data)
        stock_list.append(stock)
    return stock_list


def deal_stock() -> List[Stock]:
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
    deal_data = []
    stock_list = get_stock()
    for stock in stock_list:
        # 将str的件数转化为整数
        CANSENDNUMBER = int(stock.CANSENDNUMBER)
        # 将str的可发重量先转化为浮点型*1000在四舍五入后转为整数 千克
        CANSENDWEIGHT = int(round(float(stock.CANSENDWEIGHT) * 1000))
        if float(stock.CANSENDWEIGHT) <= 32.0:
            stock_copy = copy.deepcopy(stock)
            stock_copy.CANSENDWEIGHT = CANSENDWEIGHT
            stock_copy.CANSENDNUMBER = CANSENDNUMBER
            deal_data.append(stock_copy)
        else:
            # 件重是千克单位
            per_weight = CANSENDWEIGHT / CANSENDNUMBER
            # 32吨最多能有几件向下取整
            num = 32000 // per_weight
            if num == 0:
                continue
            # CANSENDNUMBER一共可以分几组
            group_num = int(CANSENDNUMBER // num)
            # 余数
            remainder = CANSENDNUMBER % num
            if group_num > 0:
                for j in range(group_num):
                    stock_copy = copy.deepcopy(stock)
                    stock_copy.CANSENDWEIGHT = int(round(per_weight * num))
                    stock_copy.CANSENDNUMBER = int(num)
                    deal_data.append(stock_copy)
            if remainder == 0:
                continue
            stock_copy = copy.deepcopy(stock)
            stock_copy.CANSENDWEIGHT = int(round(per_weight * remainder))
            stock_copy.CANSENDNUMBER = int(remainder)
            deal_data.append(stock_copy)
    return deal_data





deal_stock()
