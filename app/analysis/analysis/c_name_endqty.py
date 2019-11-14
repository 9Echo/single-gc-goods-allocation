import json


def c_name_endqty():
    # 读取json数据
    with open('E:\JC\json.txt', 'r') as f:
        datas = json.loads(f.read())
    # 获取品种列表
    list = ['热镀', '热镀1', 'QF热镀管', '燃气专用钢管']
    res_dic = {}
    for i in datas["data"]["list"]:
        # print(i)
        in_dic = {}
        if i['cname'] in list:
            if i['cname'] not in res_dic:
                # 添加品种
                res_dic[i['cname']] = []
                # 添加数据（规格：[除法根重，公式根重]）
                add_division_and_formula(i, in_dic, res_dic)
            else:
                add_division_and_formula(i, in_dic, res_dic)
    # 输出结果
    for res in res_dic.items():
        print(res)


def add_division_and_formula(i, in_dic, res_dic):
    if float(i['zg00']) != 0:
        division = float(i['endqty']) / float(i['zg00'])
    else:
        division = 0
    formula = formula_number(i['itemid'])
    in_dic[i['itemid']] = [division, formula]
    # print(in_dic) 出现4次
    for j in in_dic:
        if j not in res_dic[i['cname']]:
            res_dic[i['cname']].append(in_dic)


def formula_number(itemid):
    '''
    :param itemid: 规格, '020021*2.75*6000'
    :return: 返回公式计算的根重
    '''
    # 公式：(外径-壁厚)*壁厚*0.02466*1.02=米重*6米*整件支数=件重
    item = itemid.split('*')
    outside = float(item[0][3:])
    thick = float(item[1])
    length = float(item[2])/1000
    weight = (outside-thick)*thick*0.02466*1.02*length
    return weight


if __name__ == '__main__':
    c_name_endqty()