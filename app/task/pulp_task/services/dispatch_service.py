# -*- coding: utf-8 -*-
# @Time    : 2020/02/01
# @Author  : shaoluyu
import copy
import math
from threading import Thread

from app.analysis.rules import product_type_rule
from app.main.entity.delivery_item import DeliveryItem
from app.main.entity.delivery_sheet import DeliverySheet
from app.main.services import redis_service
from app.task.pulp_task.analysis.rules import scipy_optimize, pulp_solve
from app.utils import weight_calculator
from app.utils.uuid_util import UUIDUtil
from model_config import ModelConfig
from tests import test_package


def dispatch(order):
    """根据订单执行分货
    """
    product_type = None
    delivery_items = []
    new_max_weight = 0
    # product_weight = {}
    for item in order.items:
        di = DeliveryItem()
        if not product_type:
            product_type = item.product_type
            if product_type in ModelConfig.RD_LX_GROUP:
                new_max_weight = ModelConfig.RD_LX_MAX_WEIGHT
        di.product_type = item.product_type
        di.spec = item.spec
        di.quantity = item.quantity
        di.free_pcs = item.free_pcs
        di.item_id = item.item_id
        di.material = item.material
        di.f_whs = item.f_whs
        di.f_loc = item.f_loc
        di.max_quantity = ModelConfig.ITEM_ID_DICT.get(di.item_id[:3])
        # 修改成了一件的体积占比
        di.volume = 1 / di.max_quantity if di.max_quantity else 0
        di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)

        # product_weight[(item.product_type, item.item_id)] = product_weight.get((item.product_type, item.item_id), 0) + di.weight

        di.one_quantity_weight = weight_calculator.calculate_weight(di.product_type, di.item_id, 1, 0)
        di.one_free_pcs_weight = weight_calculator.calculate_weight(di.product_type, di.item_id, 0, 1)
        # di.one_quantity_weight = weight_calculator.get_one_weight(di.item_id, 1, 0)
        # di.one_free_pcs_weight = weight_calculator.get_one_weight( di.item_id, 0, 1)
        di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)
        # 如果遇到计算不出来的明细，返回0停止计算
        if di.weight == 0:
            sheet = DeliverySheet()
            sheet.weight = '0'
            sheet.items = [di]
            return sheet
        # 如果该明细有件数上限并且单规格件数超出，进行切单
        delivery_items.append(di)

    # 提货单子项信息字典
    obj_dict = {}
    # 每件对应的子项索引
    obj_index_list = []
    # 每件对应的重量
    weight_list = []
    # 每件对应的体积占比
    volume_list = []
    # 散根单件重量查询字典
    free_pcs_weight_dict = {}
    # 构建信息字典,k  下标  v   子项对象
    for i in range(len(delivery_items)):
        obj_dict[i] = delivery_items[i]
    # 构建索引、重量、体积序列
    for k, v in obj_dict.items():
        for i in range(v.quantity):
            obj_index_list.append(k)
            weight_list.append(v.one_quantity_weight)
            volume_list.append(v.volume)
        for i in range(v.free_pcs):
            obj_index_list.append(k)
            weight_list.append(v.one_free_pcs_weight)
            volume_list.append(0)
            free_pcs_weight_dict['{},{},{}'.format(v.item_id, v.material, v.f_loc)] = v.one_free_pcs_weight
    # 构建目标序列
    value_list = copy.deepcopy(weight_list)
    load_task_id = 0
    batch_no = UUIDUtil.create_id("ba")
    # 结果集
    sheets = []

    while weight_list:
        load_task_id += 1
        # plup求解，得到选中的下标序列
        result_index_list = pulp_solve.pulp_pack(weight_list, volume_list, value_list, new_max_weight)
        # 下标减少量
        temp = 0
        for i in result_index_list:
            sheet = DeliverySheet()
            i -= temp
            # item = DeliveryItem()
            item = copy.deepcopy(obj_dict.get(obj_index_list[i]))
            item.weight = weight_list[i]
            item.volume = volume_list[i]

            if free_pcs_weight_dict.get('{},{},{}'.format(item.item_id, item.material, item.f_loc)) \
                    and weight_list[i] \
                    == free_pcs_weight_dict.get('{},{},{}'.format(item.item_id, item.material, item.f_loc)):
                item.quantity = 0
                item.free_pcs = 1
                item.total_pcs = weight_calculator.calculate_pcs(item.product_type, item.item_id, 0, 1)
            else:
                item.quantity = 1
                item.free_pcs = 0
                item.total_pcs = weight_calculator.calculate_pcs(item.product_type, item.item_id, 1, 0)
            sheet.items.append(item)
            # 3、补充发货单的属性
            sheet.batch_no = batch_no
            sheet.customer_id = order.customer_id
            sheet.salesman_id = order.salesman_id
            sheet.weight = item.weight
            sheet.total_pcs = item.total_pcs
            sheet.volume = item.volume
            sheet.type = 'weight_first'
            sheet.load_task_id = load_task_id
            sheets.append(sheet)
            weight_list.pop(i)
            volume_list.pop(i)
            value_list.pop(i)
            obj_index_list.pop(i)
            temp += 1
    # 归类合并
    combine_sheets(sheets)
    # 将推荐发货通知单暂存redis
    Thread(target=redis_service.set_delivery_list, args=(sheets,)).start()
    return sheets


def combine_sheets(sheets):
    """合并因拼单被打散的发货单
    合并场景1：品类和物资代码相同的子发货单合并为1个子发货单
    合并场景2：品类相同物资代码不同的子发货单合并为1个发货单
    合并场景3：品类不同但是同属于一个similar group内的子发货单合并为1个发货单
    合并后如果被合并的发货单中没有剩余子单则删除该发货单
    """
    # 先根据车次号将发货单分组，然后对每组内发货单进行合并
    load_task_dict = {}
    for sheet in sheets:
        load_task_dict.setdefault(sheet.load_task_id, []).append(sheet)
    for load_task_id, sheet_group in load_task_dict.items():
        product_dict = {}
        for current in sheet_group:
            source = None
            # 取出当前组内的发货单，根据发货单中第一个子单的品类映射到product_dict上，每个品类对应的发货单作为合并的母体
            product_type = product_type_rule.get_product_type(current.items[0])
            if not product_dict.__contains__(product_type):
                product_dict[product_type] = current
                source = current
            else:
                source = product_dict[product_type]
                # 先将current的所有子单合并到source中，然后从sheets中删除被合并的发货单
                source.items.extend(current.items)
                source.weight += current.weight
                source.total_pcs += current.total_pcs
                source.volume += current.volume
                sheets.remove(current)
            # 再判断物资代码是否相同，如果相同则认为同一种产品，将子单合并
            item_id_dict = {}
            for citem in copy.copy(source.items):
                # 如果发现重量为0的明细，移除
                if citem.weight == 0:
                    source.items.remove(citem)
                if not item_id_dict.__contains__('{},{},{}'.format(citem.item_id, citem.material, citem.f_loc)):
                    item_id_dict['{},{},{}'.format(citem.item_id, citem.material, citem.f_loc)] = citem
                else:
                    sitem = item_id_dict['{},{},{}'.format(citem.item_id, citem.material, citem.f_loc)]
                    sitem.quantity += citem.quantity
                    sitem.free_pcs += citem.free_pcs
                    sitem.total_pcs += citem.total_pcs
                    sitem.weight += citem.weight
                    sitem.volume += citem.volume
                    source.items.remove(citem)
        # 对当前车次做完合并后，重新对单号赋值
        current_sheets = list(filter(lambda i: i.load_task_id == load_task_id, sheets))
        doc_type = '提货单'
        no = 0
        for sheet in current_sheets:
            no += 1
            sheet.delivery_no = doc_type + str(load_task_id) + '-' + str(no)
            for j in sheet.items:
                j.delivery_no = sheet.delivery_no
                j.weight = weight_calculator.calculate_weight(j.product_type, j.item_id, j.quantity, j.free_pcs)
            sheet.weight = sum(i.weight for i in sheet.items)
