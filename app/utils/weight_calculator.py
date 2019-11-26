# -*- coding: utf-8 -*-
# @Time    : 2019/11/25
# @Author  : biyushuang
from app.main.dao.weight_calculator_dao import weight_calculator_dao
from app.main.dao.base_dao import BaseDao
import traceback
import time


def weight_calculator(test_list):
    """
    # 外径、壁厚、长度、系数、根/件数
    # print(i["JM_D"], i["JM_P"], i["VER_L"], i["GS_XS"], i["GS_PER"])
    输入数据：品名、规格、件数、散根数
    :return: t_calculator_item中有此品种规格的记录，则返回:理重weight，反之返回:None
    """
    # weight = 0
    print('input:  ', test_list)
    data = weight_calculator_dao.get_data_from_table(test_list)
    if len(data) != 0:
        for i in data:
            if i["CNAME"] == test_list[0] and i["ITEMID"] == test_list[1]:
                # 根重
                weight_one = get_weight_of_each_root(i)
                weight = weight_one * int(test_list[2]) * i["GS_PER"] + weight_one * int(test_list[3])
        return weight


def get_weight_of_each_root(item):
    """
    :param item: 需要计算理重的数据在数据库中对应的那条数据
    :return:根重
    """
    # 数据预处理
    outside = float(item["JM_D"])  # 外径
    thick = float(item["JM_P"])  # 壁厚
    length = float(item["VER_L"])  # 长度
    h_list = ['焊管', '焊管 1']
    f_list = ['方矩管', '热镀方矩管']
    r_list = ['热镀', '热镀1', 'QF热镀管', '燃气专用钢管', '热度']
    # 计算未乘系数的米重
    if test_list[0] == '螺旋焊管':
        weight_item = (outside - (thick - 0.9)) * (thick - 0.9) * 0.0246615
    elif test_list[0] in h_list:
        weight_item = (outside - thick) * thick * 0.02466
    elif test_list[0] in f_list:
        weight_item = ((outside - 3) / 3.14159 - thick) * thick * 0.02466
    elif test_list[0] in r_list:
        if item["GS_XS"] is None:
            coefficient = 1.02
        else:
            coefficient = float(item["GS_XS"])
        weight_item = (outside - thick) * thick * 0.02466 * coefficient
    # 计算根重
    weight_item = weight_item * length / 1000
    return weight_item


if __name__ == '__main__':
    print('start_time: ', time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))
    test_list = ['热镀1', '257088*2.6*6000', 5, 3]
    weight = weight_calculator(test_list)
    print('output:  ', weight)
    print('end_time: ',time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))

