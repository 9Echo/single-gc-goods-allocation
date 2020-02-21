from pulp import *


# size = [21, 11, 15, 9, 34, 25, 41, 52, 21, 11, 15, 9, 34, 25, 41, 52, 21, 11, 15, 9, 34, 25, 41, 52, 21, 11, 15, 9,
# 34, 25, 41, 52, 21, 11, 15, 9, 34, 25, 41, 52, 21, 11, 15, 9, 34, 25, 41, 52] weight = [22, 12, 16, 10, 35, 26, 42,
# 53, 22, 12, 16, 10, 35, 26, 42, 53, 22, 12, 16, 10, 35, 26, 42, 53, 22, 12, 16, 10, 35, 26, 42, 53, 22, 12, 16, 10,
# 35, 26, 42, 53, 22, 12, 16, 10, 35, 26, 42, 53]


def package(weight_list, volume_list, value_list):
    capacity = 33000
    r = range(len(weight_list))
    m = LpProblem(sense=LpMaximize)  # 数理モデル
    x = [LpVariable('x%d' % i, cat=LpBinary) for i in r]  # 変数
    m += lpDot(value_list, x)  # 目的関数
    m += lpDot(weight_list, x) <= capacity  # 制約
    # m += lpDot(volume_list, x) >= 1.17
    m += lpDot(volume_list, x) <= 1.18
    m.solve()
    print((value(m.objective), [i for i in r if value(x[i]) > 0.5]))
    # result_index_list = []
    # # result_weight_list = []
    # # result_volume_list = []
    # # result_value_list = []
    # print(len(result_index_list))
    return [i for i in r if value(x[i]) > 0.5]
