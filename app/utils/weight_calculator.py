# -*- coding: utf-8 -*-
# @Time    : 2019/11/25
# @Author  : biyushuang
from app.main.dao.weight_calculator_dao import weight_calculator_dao
import time


def weight_calculator(cname, itemid, pack_num, free_num=0):
    """
    输入数据：品名:cname、规格:itemid、件数:pack_num、散根数:free_num
    :return: t_calculator_item中有此品种规格的记录，则返回:理重weight，反之返回:None
    """
    # weight = 0
    print('input:  ', cname, itemid, pack_num, free_num)
    data = weight_calculator_dao.get_data_from_table(cname, itemid)
    # 外径、壁厚、长度、系数、根 / 件数
    # i["JM_D"], i["JM_P"], i["VER_L"], i["GS_XS"], i["GS_PER"]
    if len(data) != 0:
        for i in data:
            if i["CNAME"] == cname and i["ITEMID"] == itemid:
                # 根重
                weight_one = get_weight_of_each_root(i, cname)
                weight = weight_one * int(pack_num) * i["GS_PER"] + weight_one * int(free_num)
        return weight


def get_weight_of_each_root(item, cname):
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
    if cname == '螺旋焊管':
        weight_item = (outside - (thick - 0.9)) * (thick - 0.9) * 0.0246615
    elif cname in h_list:
        weight_item = (outside - thick) * thick * 0.02466
    elif cname in f_list:
        weight_item = ((outside - 3) / 3.14159 - thick) * thick * 0.02466
    elif cname in r_list:
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
    # weight = weight_calculator('热镀1', '257088*2.6*6000', 5, 3)
    weight = weight_calculator('热镀1', '257088*2.6*6000', 5)
    # weight = weight_calculator(pack_num=5, cname='热镀1', itemid='257088*2.6*6000', free_num=3)
    # weight = weight_calculator(pack_num=5, cname='热镀1', itemid='257088*2.6*6000')
    print('output:  ', weight)
    print('end_time: ', time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))

