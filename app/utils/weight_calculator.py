# -*- coding: utf-8 -*-
# @Time    : 2019/11/25
# @Author  : biyushuang
import time
from app.main.entity.delivery_item import DeliveryItem
from app.main.dao.weight_calculator_dao import weight_calculator_dao


def weight_list_calculator(calculate_list):
    '''
    :param calculate_list: 需要得到根重的delivery_item列表
    :return: 得到根重的delivery_item列表
    '''
    item_list = weight_calculator_dao.get_data_list_from_table(calculate_list)
    print(item_list)
    for i in calculate_list:
        for item in item_list:
            if i.item_id == item["ITEMID"]:
                # 计算根重
                if item["GBGZL"] is not None and float(item["GBGZL"]) > 0 and item["GS_PER"] is not None:
                    i.weight = float(item["GBGZL"]) * (float(i.quantity) * float(item["GS_PER"]) + float(i.free_pcs))
                else:
                    i.weight = None
                    # weight_one = get_weight_of_each_root(i)
                # i.weightone = round(weight_one)
    return calculate_list


def calculate_pcs(cname, itemid, pack_num=0, free_num=0):
    """
    :return: t_calculator_item中有此品种规格的记录，则返回:总根数，反之返回:0
    """
    data = weight_calculator_dao.get_data_from_table(cname, itemid)
    total_pcs = 0
    if len(data) != 0:
        i = data[0]
        # 根重
        if i["GS_PER"] and float(i["GS_PER"]) > 0:
            pcs = int(i["GS_PER"])
        total_pcs = int(pack_num) * pcs + int(free_num)
    return total_pcs


def calculate_weight(cname, itemid, pack_num=0, free_num=0):
    """
    # 外径、壁厚、长度、系数、根 / 件数
    # i["JM_D"], i["JM_P"], i["VER_L"], i["GS_XS"], i["GS_PER"]
    输入数据：品名:cname、规格:itemid、件数:pack_num、散根数:free_num
    :return: t_calculator_item中有此品种规格的记录，则返回:理重weight，反之返回:0
    """
    data = weight_calculator_dao.get_data_from_table(cname, itemid)
    weight = 0
    if len(data) != 0:
        i = data[0]
        # 根重
        weight_one = 0
        if i["GBGZL"] is not None and float(i["GBGZL"]) > 0:
            weight_one = float(i["GBGZL"])
        # else:
        #     weight_one = get_weight_of_each_root(i)
        # if pack_num == 0:
        #     weight = round(weight_one) * int(free_num)
        GS_PER = i["GS_PER"] if i["GS_PER"] else 0
        weight = round(weight_one * int(pack_num) * GS_PER + weight_one * int(free_num))
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
    if item["CNAME"] == '螺旋焊管':
        weight_item = (outside - (thick - 0.9)) * (thick - 0.9) * 0.0246615
    elif item["CNAME"] in h_list:
        weight_item = (outside - thick) * thick * 0.02466
    elif item["CNAME"] in f_list:
        weight_item = ((outside - 3) / 3.14159 - thick) * thick * 0.02466
    elif item["CNAME"] in r_list:
        if item["GS_XS"] is None:
            coefficient = 1.02
        else:
            coefficient = float(item["GS_XS"])
        weight_item = (outside - thick) * thick * 0.02466 * coefficient
    # 计算根重
    weight_item = weight_item * length / 1000
    return weight_item


# def update_gbgzl():
#     # 将表t_calculator_item中的GBGZL<=0的和为空的列替换为公式计算的根重
#     list_all = weight_calculator_dao.get_all_data()
#     update_list = []
#     for i in list_all:
#         if i["GBGZL"] is None or float(i["GBGZL"]) <= 0:
#             i["GBGZL"] = round(get_weight_of_each_root(i), 2)
#             update_list.append(i)
#     print(update_list)
#     weight_calculator_dao.update_gbgzl(update_list)


# def update_jmd():
#     # 计算出数据库中方矩管和热镀方矩管的外径，并更新JM_D列的数据
#     data = weight_calculator_dao.get_data_from_table()
#     print(data)
#     update_list = []
#     for i in data:
#         items = i["ITEMID"].split('*')
#         length = float(items[0][3:])
#         width = float(items[1])
#         i["JM_D"] = 2*(length + width)
#         update_list.append(i)
#     print(update_list)
#     weight_calculator_dao.update_data(update_list)


# def check_item():
#     # 确认根重的选取
#     file_name = 'E:/JC/test.xls'
#     value_list = read_excel(file_name)
#     check_result_list = []
#     j = 0
#     for i in value_list:
#         weight = calculate(i[1], i[0], 0, 1)
#         j = j+1
#         if weight is not None and i[2] is not None:
#             i_weight = abs(i[2] - weight)
#             print(j, ':',[i[0], i[1], i[3], i[4], i[5], i[2], weight, i_weight])
#             check_result_list.append([i[0], i[1], i[3], i[4], i[5], i[2], weight, i_weight])
#     # print(check_result_list)
#     filename = 'E:\JC\check_test_result.xlsx'
#     write_excel_xls(filename, check_result_list)


# def read_excel(filename):
#     # 打开excel文件，返回实例对象
#     excel = xlrd.open_workbook(filename)
#     # 获取某一个sheet对象
#     sheet_index = excel.sheet_by_index(0)
#     # 获取总行数
#     row_num = sheet_index.nrows
#     col_num = sheet_index.ncols
#     col_num = col_num - 1
#     # print(row_num, col_num)
#     value_list = []
#     for i in range(1, row_num):
#         row_v = sheet_index.row_values(i)
#         row_v = [None if row == "" else row for row in row_v]  # None在数据库显示为Null
#         value_list.append(row_v)
#     return value_list


# def write_excel_xls(filename, data_list):
#     workbook = xlsxwriter.Workbook(filename)  # 创建一个excel文件
#     worksheet = workbook.add_worksheet()  # 创建一个sheet
#
#     # 将数据写入第 i 行，第 j 列
#     i = 0
#     for data in data_list:
#         for j in range(len(data)):
#             worksheet.write(i, j, str(data[j]))
#         i = i + 1
#     workbook.close()


if __name__ == '__main__':
    # update_gbgzl()
    # print('start_time: ', time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))
    # weight = weight_calculator('螺旋焊管', '0CH660*10.0*6000', 0, 1)
    # weight = weight_calculator('热镀1', '257088*2.6*6000', 5)
    # # weight = weight_calculator(pack_num=5, cname='热镀1', itemid='257088*2.6*6000', free_num=3)
    # # weight = weight_calculator(pack_num=5, cname='热镀1', itemid='257088*2.6*6000')
    # print('output:  ', weight)
    # print('end_time: ', time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))
    # check_item()
    # if i.free_pcs is not None and (i.quantity == 0 or i.quantity is None):
    #     weight = round(weight_one) * int(i.free_pcs)
    # elif i.quantity is not None:
    #     if i.free_pcs is None:
    #         i.free_pcs = 0
    #     weight = round(weight_one * int(i.quantity) * item["GS_PER"] + weight_one * int(i.free_pcs))
    # item_dic[i.delivery_item_no] = weight
    # result_list.append(item_dic)
    item1 = DeliveryItem(
        {'delivery_item_no': '001', 'product_type': '螺旋焊管', 'item_id': '0CH660*10.0*6000', 'quantity': 0})
    item2 = DeliveryItem({'delivery_item_no': '002', 'product_type': '焊管', 'item_id': '010020.5*1.8*5950'})
    item3 = DeliveryItem(
        {'delivery_item_no': '003', 'product_type': '方矩管', 'item_id': '054025*025*0.9*5990', 'quantity': 1})
    calculate_list = [item2, item3]
    result_list = weight_list_calculator(calculate_list)
    for i in result_list:
        print(i.weightone)
    # print('end_time: ', time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))
