def get_json_before(order):
        """
        处理json数据 得到开单前的件数和散根
        :param order: 传入的json数据
        :return: product_info: 存放货物的件数和散根数
        """
        items = order.items
        product_info = {}
        for i in items:
            if (i.product_type, i.item_id) not in product_info:
                product_info[(i.product_type, i.item_id)] = {}
            product_info[(i.product_type, i.item_id)]["quantity"] = product_info[(i.product_type, i.item_id)].get("quantity", 0) + i.quantity
            product_info[(i.product_type, i.item_id)]["free_pcs"] = product_info[(i.product_type, i.item_id)].get("free_pcs", 0) + i.free_pcs
        return product_info


def get_product_info_after(sheets):
    """
    处理生成的sheets数据，得到车重、车辆的体积占比、货物的件数和散根数
    :param sheets: 传入的sheets数据
    :return: product_info: 存放货物件数和散根数
    :return: car_info: 存放车辆的载重和体积占比
    """
    product_info = {}
    car_info = {}
    temp_boolean = False
    for sheet in sheets:
        if sheet.load_task_id not in car_info:
            car_info[sheet.load_task_id] = {}
        car_info[sheet.load_task_id]["weight"] = sheet.weight
        sheet_items = sheet.items
        for item in sheet_items:
            # car_info[sheet.load_task_id]["product_info"]
            if item.product_type in ["热镀", "螺旋焊管", "QF热镀管"]:
                temp_boolean = True
            if (item.product_type, item.item_id) not in product_info:
                product_info[(item.product_type, item.item_id)] = {}
            car_info[sheet.load_task_id]["volume"] = car_info[sheet.load_task_id].get("volume", 0) + float(item.volume)
            product_info[(item.product_type, item.item_id)]["quantity"] = product_info[(item.product_type, item.item_id)].get("quantity", 0) + int(item.quantity)
            product_info[(item.product_type, item.item_id)]["free_pcs"] = product_info[(item.product_type, item.item_id)].get("free_pcs", 0) + int(item.free_pcs)
            product_info[(item.product_type, item.item_id)]["weight"] = product_info[(item.product_type, item.item_id)].get("weight", 0) + int(item.weight)
    for key in car_info:
        car_info[key]["include_ReDu_And_LuoXuan"] = temp_boolean
    return product_info, car_info


def judge_info(dict1, dict2, dict3, sum_weight_before, weight=33000):
        """
        比较两个货物信息字典对应key的数量差异
        及对dict3：计算总货物重量, 比较体积占比
        :param dict1:分货之前货物信息 包括件数和散根数 type:dict
        :param dict2:分货之后货物信息 包括件数和散根数 type:dict
        :param dict3:分货之后车载信息 包括体积占比是否装载了热镀和螺旋 type:dict
        :param sum_weight_before:分货之前车载的货物信息重量 type:dict
        :param weight:载重上限
        :return: error: 发生错误的数据 type:dict
        """
        error = {}
        for key in dict2:
            if dict1[key]["quantity"] - dict2[key]["quantity"] != 0:
                if key not in error:
                    error[key] = {}
                error[key]["quantity"] = abs(dict1[key]["quantity"] - dict2[key]["quantity"])
            if dict1[key]["free_pcs"] - dict2[key]["free_pcs"] != 0:
                error[key]["free_pcs"] = abs(dict1[key]["free_pcs"] - dict2[key]["free_pcs"])
            if abs(float(dict2[key]["weight"]) - float(sum_weight_before[key])) > 1.0:
                error[key] = [sum_weight_before[key], dict2[key]["weight"]]
        for i in dict3:
            if float(dict3[i]["volume"]) > 1.18:
                error["volume_error"] = [i, dict3[i]["volume"]]
            if weight == 33000:
                if dict3[i]["include_ReDu_And_LuoXuan"]:
                    weight += 1000
            if float(dict3[i]["weight"]) > weight:
                error["weight_error"] = [i, dict3[i]["weight"], weight]
        return error