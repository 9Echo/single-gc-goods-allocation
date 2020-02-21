# -*- coding: utf-8 -*-
# @Time    : 2020/01/19
# @Author  : shaoluyu
import math

from scipy.optimize import minimize, Bounds

from app.utils import collection_util
import numpy as np

volume = [1/10000, 1/34, 1/22, 1/22, 1/34]
one_weight = [1.067, 0.751, 1.488, 0.641, 0.815]
order_j = [50, 40, 40, 40, 30]
max_weight = 32.5
max_volume = 1.18


def my_minimize(one_volume, one_weight, order_j, max_weight, max_volume, car_count, product_type_count):
    # 初始化矩阵
    x = np.zeros((car_count, product_type_count))
    args = (one_volume, one_weight, order_j, max_weight, max_volume, car_count, product_type_count)
    # 添加约束
    cons = con(args)
    # bnds = ()
    # for i in range(car_count * product_type_count):
    #     bnds += ((0, None),)
    # 非线性规划求最优解
    return minimize(fun(args), x, method='SLSQP', bounds=Bounds(lb=0, ub=50, keep_feasible=True), constraints=cons)


def con(args):
    # 约束条件 分为eq 和ineq
    # eq表示 函数结果等于0 ； ineq 表示 表达式大于等于0
    one_volume, one_weight, order_j, max_weight, max_volume, car_count, product_type_count = args
    cons = ()
    # 添加件数被分配完的约束
    for i in range(product_type_count):
        cons += ({'type': 'eq',
                  'fun': lambda x: sum([x[j][i] for j in range(car_count)]) - order_j[i]},)
    # 添加车次总重量不超过最大载重、车次总体积占比不超过最大体积占比的约束
    for i in range(car_count):
        cons += ({'type': 'ineq', 'fun': lambda x: max_weight - sum(
            [x[i][j] * one_weight[j] for j in range(product_type_count)])},)
        cons += ({'type': 'ineq', 'fun': lambda x: max_volume - sum(
            [x[i][j] * (one_volume[j]) for j in range(product_type_count)])},)

    return cons


def fun(args):
    one_volume, one_weight, order_j, max_weight, max_volume, car_count, product_type_count = args

    # 目标函数，残差平方和最小
    def my_method(x):
        y = 0
        for i in range(car_count):
            y += (max_weight - collection_util.dot(x[i], one_weight)) ** 2
        return y

    return my_method


if __name__ == "__main__":
    # 定义常量值
    # args = (2, 1, 3, 4)  # a,b,c,d
    # 设置参数范围/约束条件
    # args = (volume, one_weight, order_j, max_weight, max_volume, 6, 5)  # x1min, x1max, x2min, x2max
    # cons = con(args)
    # 设置初始猜测值   6*5
    # x0 = np.zeros((6, 5))
    # x0 = np.asarray((0, 0, 0))
    # bnds = ()
    # for i in range(0, 30):
    #     bnds += ((0, None),)

    res = my_minimize(volume, one_weight, order_j, max_weight, max_volume, 6, 5)
    print(res.fun)
    print(res.success)
    # print(res.x)
    result = res.x.reshape(6, 5)
    print(result)
    print(result.sum(axis=0))
    result = np.around(result)
    print(result)
    for i in range(6):
        print('第' + str(i + 1) + '车载重              体积占比')
        print(result[i, 0] * one_weight[0] + result[i, 1] * one_weight[1]
              + result[i, 2] * one_weight[2] + result[i, 3] * one_weight[3] + result[i, 4] * one_weight[4],
              result[i, 0] * 1 / volume[0] + result[i, 1] * 1 / volume[1]
              + result[i, 2] * 1 / volume[2] + result[i, 3] * 1 / volume[3] + result[i, 4] * 1 / volume[4])
    print(result.sum(axis=0))
