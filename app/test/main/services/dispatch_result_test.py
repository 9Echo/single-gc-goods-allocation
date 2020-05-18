import operator


def collect_difference(type,sheets):
    """根据不同情况下分货结果统计车次数量、残差平方和、被拆分物资代码数量
    """
    results_dict={}
    results_dict["type"]=type
    results_item_dict={}
    # 统计车次数量(最大车次)
    truck_number=sheets[len(sheets)-1].load_task_id
    results_item_dict["truck_number"]=truck_number

    #
    for item in sheets:
        item.weight_difference=abs(item.weight-33000)/1000

    #  根据平方差排序
    cmpfun = operator.attrgetter("weight_difference")  # 参数为排序依据的属性，可以有多个，这里优先id，使用时按需求改换参数即可
    sheets.sort(key=cmpfun)

    # 统计残差平方和,汇总sheet_items
    sheet_items_list=[]
    sum_squared_differneces=0.0
    for i in range(0,len(sheets)-1):
        item_difference=abs(sheets[i].weight-33000)/1000
        item_difference=item_difference*item_difference
        sum_squared_differneces=sum_squared_differneces+item_difference
        #添加元素
        for item in sheets[i].items:
            sheet_items_list.append(item)
    results_item_dict["sum_squared_differneces"] = sum_squared_differneces

    #统计被拆分物资代码数量
    collect_dict={}
    for item in sheet_items_list:
        if item.item_id not in collect_dict.keys():
            collect_dict[item.item_id]=1
        else:
            collect_dict[item.item_id] = collect_dict[item.item_id]+1

    # 统计大于等于2的个数
    split_item_num=0
    for key in collect_dict:
        if collect_dict[key]>=2:
            split_item_num=split_item_num+1

    results_item_dict["split_item_num"] = split_item_num
    results_dict["data"]=results_item_dict
    return  results_dict
