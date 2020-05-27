# -*- coding: utf-8 -*-
# @Time    : 2020/02/01
# @Author  : shaoluyu
import copy
from threading import Thread
from flask import g
from app.main.pipe_factory.rule import product_type_rule
from app.main.pipe_factory.entity.delivery_item import DeliveryItem
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.main.pipe_factory.service import redis_service
from app.main.pipe_factory.service.create_delivery_item_service import CreateDeliveryItem
from app.main.pipe_factory.service.replenish_property_service import replenish_property
from app.task.pulp_task.analysis.rules import pulp_solve
from app.util import weight_calculator
from app.util.uuid_util import UUIDUtil
from model_config import ModelConfig


def dispatch(order):
    """根据订单执行分货
    """
    # 1、将订单项转为发货通知单子单的list
    delivery_item_list= CreateDeliveryItem(order)
    # delivery_item_list.is_success=False证明有计算异常,返回一张含有计算出错子项的sheet
    if not delivery_item_list.success:
        return delivery_item_list.failsheet()
    else:
        delivery_item_weight_list,new_max_weight = delivery_item_list.weight()  # 调用weight()，即重量优先来处理

    weight_list, volume_list, value_list = create_variable_list(delivery_item_weight_list)
    sheets = call_pulp_solve(weight_list, volume_list, value_list, delivery_item_weight_list, new_max_weight)

    # 3、补充发货单的属性
    batch_no = UUIDUtil.create_id("ba")
    replenish_property(sheets, order,batch_no)

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
                    continue
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


def create_sheet_item(order):
    """
    创建提货单子项
    :param order:
    :return:
    """
    product_type = None
    delivery_items = []
    new_max_weight = 0
    for item in order.items:
        if not product_type:
            product_type = item.product_type
            if product_type in ModelConfig.RD_LX_GROUP:
                new_max_weight = g.RD_LX_MAX_WEIGHT

        for _ in range(item.quantity):
            di = DeliveryItem()
            di.product_type = item.product_type
            di.spec = item.spec
            di.quantity = 1
            di.free_pcs = 0
            di.item_id = item.item_id
            di.material = item.material
            di.f_whs = item.f_whs
            di.f_loc = item.f_loc
            di.volume = 1 / di.max_quantity if di.max_quantity else 0.001
            di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)
            di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)
            # 如果遇到计算不出来的明细，返回0停止计算
            if di.weight == 0:
                if di.weight == 0:
                    return [di], new_max_weight, False
            delivery_items.append(di)
        for _ in range(item.free_pcs):
            di = DeliveryItem()
            di.product_type = item.product_type
            di.spec = item.spec
            di.quantity = 0
            di.free_pcs = 1
            di.item_id = item.item_id
            di.material = item.material
            di.f_whs = item.f_whs
            di.f_loc = item.f_loc
            di.volume = 0
            di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)
            di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)
            delivery_items.append(di)
    return delivery_items, new_max_weight, True


def create_variable_list(delivery_items):
    """

    :return:
    """
    weight_list = []
    # 每件对应的体积占比
    volume_list = []
    for i in delivery_items:
        weight_list.append(i.weight)
        volume_list.append(i.volume)
    # 构建目标序列
    value_list = copy.deepcopy(weight_list)
    return weight_list, volume_list, value_list


def call_pulp_solve(weight_list, volume_list, value_list, delivery_items, new_max_weight):
    """

    :param delivery_items:
    :param weight_list:
    :param volume_list:
    :param new_max_weight:
    :param value_list:
    :return:
    """
    load_task_id = 0
    batch_no = UUIDUtil.create_id("ba")
    # 结果集
    sheets = []
    while delivery_items:
        load_task_id += 1
        # plup求解，得到选中的下标序列
        result_index_list, value = pulp_solve.pulp_pack(weight_list, volume_list, value_list, new_max_weight)

        #理这里分出来的result_index_list的物资应该合起来是一车上的物品，但是由于可能有不同品类的货，所以不能合并在一张发货单上
        for i in sorted(result_index_list, reverse=True):
            sheet = DeliverySheet()
            item = delivery_items[i]
            sheet.items.append(item)

            # 设置提货单总体积占比
            sheet.volume = item.volume
            sheet.type = 'weight_first'
            #重量优先每次都能分车，所以模型跑完就不用后续分车了
            sheet.load_task_id = load_task_id
            sheets.append(sheet)
            weight_list.pop(i)
            volume_list.pop(i)
            value_list.pop(i)
            delivery_items.pop(i)
    return sheets
