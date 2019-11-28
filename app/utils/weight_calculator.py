# -*- coding: utf-8 -*-
# @Time    : 2019/11/25
# @Author  : biyushuang
from app.main.dao.weight_calculator_dao import weight_calculator_dao
import time
import xlrd
import xlsxwriter


def weight_calculator(cname, itemid, pack_num, free_num=0):
    """
    # 外径、壁厚、长度、系数、根 / 件数
    # i["JM_D"], i["JM_P"], i["VER_L"], i["GS_XS"], i["GS_PER"]
    输入数据：品名:cname、规格:itemid、件数:pack_num、散根数:free_num
    :return: t_calculator_item中有此品种规格的记录，则返回:理重weight，反之返回:None
    """
    print('input:  ', cname, itemid, pack_num, free_num)
    data = weight_calculator_dao.get_data_from_table(cname, itemid)
    print(data)
    if len(data) == 1:
        for i in data:
            if i["CNAME"] == cname and i["ITEMID"] == itemid:
                # 根重
                if i["GBGZL"] is not None and float(i["GBGZL"]) > 0:
                    weight_one = float(i["GBGZL"])
                else:
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


def check_item():
    file_name = 'E:/JC/test.xls'
    value_list = read_excel(file_name)
    check_result_list = []
    j = 0
    for i in value_list:
        weight = weight_calculator(i[1], i[0], 0, 1)
        j = j+1
        if weight is not None and i[2] is not None:
            i_weight = abs(i[2] - weight)
            print(j, ':',[i[0], i[1], i[3], i[4], i[5], i[2], weight, i_weight])
            check_result_list.append([i[0], i[1], i[3], i[4], i[5], i[2], weight, i_weight])
    # print(check_result_list)
    filename = 'E:\JC\check_test_result.xlsx'
    write_excel_xls(filename, check_result_list)


def read_excel(filename):
    # 打开excel文件，返回实例对象
    excel = xlrd.open_workbook(filename)
    # 获取某一个sheet对象
    sheet_index = excel.sheet_by_index(0)
    # 获取总行数
    row_num = sheet_index.nrows
    col_num = sheet_index.ncols
    col_num = col_num - 1
    # print(row_num, col_num)
    value_list = []
    for i in range(1, row_num):
        row_v = sheet_index.row_values(i)
        row_v = [None if row == "" else row for row in row_v]  # None在数据库显示为Null
        value_list.append(row_v)
    return value_list


def write_excel_xls(filename, data_list):
    workbook = xlsxwriter.Workbook(filename)  # 创建一个excel文件
    worksheet = workbook.add_worksheet()  # 创建一个sheet

    # 将数据写入第 i 行，第 j 列
    i = 0
    for data in data_list:
        for j in range(len(data)):
            worksheet.write(i, j, str(data[j]))
        i = i + 1
    workbook.close()


if __name__ == '__main__':
    # print('start_time: ', time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))
    weight = weight_calculator('方矩管', '052019*019*0.8*6000', 0, 1)
    # weight = weight_calculator('热镀1', '257088*2.6*6000', 5)
    # # weight = weight_calculator(pack_num=5, cname='热镀1', itemid='257088*2.6*6000', free_num=3)
    # # weight = weight_calculator(pack_num=5, cname='热镀1', itemid='257088*2.6*6000')
    print('output:  ', weight)
    # print('end_time: ', time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))
    # check_item()
    # 计算出数据库中方矩管和热镀方矩管的外径，并更新JM_D列的数据
    # data = weight_calculator_dao.get_data_from_table()
    # print(data)
    # update_list = []
    # for i in data:
    #     items = i["ITEMID"].split('*')
    #     length = float(items[0][3:])
    #     width = float(items[1])
    #     i["JM_D"] = 2*(length + width)
    #     update_list.append(i)
    # print(update_list)
    # weight_calculator_dao.update_data(update_list)

