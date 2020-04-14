from pulp import *
from flask import g
from model_config import ModelConfig


def pulp_pack(weight_list, volume_list, value_list, new_max_weight):
    capacity = new_max_weight or g.MAX_WEIGHT
    r = range(len(weight_list))
    prob = LpProblem(sense=LpMaximize)
    x = [LpVariable('x%d' % i, cat=LpBinary) for i in r]  # 変数
    prob += lpDot(value_list, x)  # 目标函数
    # 约束
    prob += lpDot(weight_list, x) <= capacity
    if volume_list:
        prob += lpDot(volume_list, x) <= ModelConfig.MAX_VOLUME
    # 解题
    prob.solve()
    # print(('车次载重' + str(value(prob.objective)) + 'kg', '选中变量' + str([i for i in r if value(x[i]) > 0.5])))
    # print(len([i for i in r if value(x[i]) > 0.5]))
    # print(len(result_index_list))
    return [i for i in r if value(x[i]) > 0.5]
