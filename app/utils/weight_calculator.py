# -*- coding: utf-8 -*-
# @Time    : 2019/11/25
# @Author  : biyushuang
from app.main.dao.weight_calculator_dao import weight_calculator_dao
from app.main.dao.base_dao import BaseDao
import traceback


def weight_calculator(test_list):
    """
    # 外径、壁厚、长度、系数、根/件数
    # print(i["JM_D"], i["JM_P"], i["VER_L"], i["GS_XS"], i["GS_PER"])
    输入数据：品名、规格、件数、散根数
    :return: 理重：weight

    """
    # weight = 0
    print('input:  ', test_list)
    data = weight_calculator_dao.get_data_from_table(test_list)
    # print(data)
    for i in data:
        if i["CNAME"] == test_list[0] and i["ITEMID"] == test_list[1]:
            # 外径、壁厚、长度、系数、根/件数
            # print(i["JM_D"], i["JM_P"], i["VER_L"], i["GS_XS"], i["GS_PER"])
            # 根重
            weight_one = get_weight_of_each_root(i)
            weight = weight_one * int(test_list[2]) * i["GS_PER"] + weight_one * int(test_list[3])
    return weight
    raise RuntimeError('input data error')


def get_weight_of_each_root(item):
    """
    :param item: 需要计算理重的数据在数据库中对应的那条数据
    :return:根重
    """
    # if item["JM_D"] is not None and item["JM_P"] is not None\
    #         and item["VER_L"] is not None and item["GS_XS"] is not None:

    # 数据预处理
    outside = float(item["JM_D"])  # 外径
    thick = float(item["JM_P"])  # 壁厚
    length = float(item["VER_L"])  # 长度
    coefficient = float(item["GS_XS"])  # 系数
    r_list = ['热镀', '热镀1', 'QF热镀管', '燃气专用钢管', '热度']
    # 计算未乘系数的米重
    if test_list[0] == '螺旋焊管':
        weight = (outside - (thick - 0.9)) * (thick - 0.9) * 0.0246615
    elif test_list[0] == '焊管':
        weight = (outside - thick) * thick * 0.02466
    elif test_list[0] == '方矩管' or test_list[0] == '热镀方矩管':
        weight = ((outside - 3) / 3.14159 - thick) * thick * 0.02466
    elif test_list[0] in r_list:
        weight = (outside - thick) * thick * 0.02466
    # 计算根重
    weight_one = weight * length / 1000 * coefficient
    return weight_one


if __name__ == '__main__':
    test_list = ['焊管', '012032*0.6*5950', 5, 3]
    weight = weight_calculator(test_list)
    print('output:  ', weight)
    # 计算出数据库中方矩管和热镀方矩管的外径，并更新JM_D列的数据
    # data = weight_calculator_dao.get_data_from_table()
    # update_list = []
    # for i in data:
    #     items = i["ITEMID"].split('*')
    #     length = float(items[0][3:])
    #     width = float(items[1])
    #     i["JM_D"] = length + width
    #     update_list.append(i)
    # weight_calculator_dao.update_data(update_list)
