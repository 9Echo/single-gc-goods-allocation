# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
import copy

from app.analysis.rules import dispatch_filter, weight_rule, product_type_rule
from app.main.entity.delivery_item import DeliveryItem
from app.main.services import redis_service
from app.utils import weight_calculator
from app.utils.uuid_util import UUIDUtil
from config import Config


def dispatch(order):
    """根据订单执行分货
    """
    # 将订单项转为发货通知单子单
    delivery_items = []
    for item in order.items:
        di = DeliveryItem()
        di.product_type = item.product_type
        di.spec = item.spec
        di.quantity = item.quantity
        di.free_pcs = item.free_pcs
        di.item_id = item.item_id
        di.material = item.material
        di.f_whs = item.f_whs
        di.f_loc = item.f_loc
        di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)
        di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)
        delivery_items.append(di)
    # 使用模型过滤器生成发货通知单
    sheets = dispatch_filter.filter(delivery_items)
    # 补充发货单的属性
    batch_no = UUIDUtil.create_id("ba")
    # 提货单号序号
    # doc_type = '提货单'
    # sheet_no = 0
    for sheet in sheets:
        # sheet_no += 1
        # sheet.delivery_no = sheet.delivery_no = doc_type + str(sheet_no)
        sheet.batch_no = batch_no
        sheet.customer_id = order.customer_id
        sheet.salesman_id = order.salesman_id
        sheet.weight = 0
        sheet.total_pcs = 0
        for di in sheet.items:
            di.delivery_item_no = UUIDUtil.create_id("di")
            # di.delivery_no = sheet.delivery_no
            sheet.weight += di.weight
            sheet.total_pcs += di.total_pcs
    # 为发货单分配车次
    dispatch_load_task(sheets)
    combine_sheets(sheets)
    # 将推荐发货通知单暂存redis
    redis_service.set_delivery_list(sheets)
    return sheets


def dispatch_load_task(sheets: list):
    """将发货单根据重量组合到对应的车次上"""

    # 根据前端要求，将车次号置成普通的数字
    task_id = 0
    doc_type = '提货单'
    # new_sheet_no = len(sheets) + 1
    left_sheets = []
    # 先为重量为空或已满的单子生成单独车次
    for sheet in sheets:
        if sheet.weight == 0 or sheet.weight >= Config.MAX_WEIGHT:
            task_id += 1
            sheet.load_task_id = task_id
        else:
            left_sheets.append(sheet)
    # 记录是否有未分车的单子
    while left_sheets:
        # print_sheets(left_sheets)
        total_weight = 0
        task_id += 1
        no = 0
        for sheet in copy.copy(left_sheets):
            total_weight += sheet.weight
            if total_weight <= Config.MAX_WEIGHT:
                # 不超重时将当前发货单装到车上
                sheet.load_task_id = task_id
                # 给当前提货单赋单号
                no += 1
                sheet.delivery_no = doc_type + str(task_id) + '-' + str(no)
                # 给明细赋单号
                for item in sheet.items:
                    item.delivery_no = sheet.delivery_no
                # 将拼车成功的单子移除
                left_sheets.remove(sheet)
                if Config.MAX_WEIGHT - total_weight < Config.TRUCK_SPLIT_RANGE:
                    # 接近每车临界值时停止本次装车
                    break
            else:
                # 超重时对发货单进行分单
                if sheet.weight < Config.TRUCK_SPLIT_RANGE:
                    # 重量不超过1吨（可配置）的发货单不分单
                    break
                else:
                    # 对满足条件的发货单进行分单
                    limit_weight = Config.MAX_WEIGHT - (total_weight - sheet.weight)
                    sheet, new_sheet = split_sheet(sheet, limit_weight)
                    if new_sheet:
                        # 分单成功时旧单放入当前车上，新单放入等待列表
                        # new_sheet_no += 1
                        sheet.load_task_id = task_id
                        # 给旧单赋单号
                        no += 1
                        sheet.delivery_no = doc_type + str(task_id) + '-' + str(no)
                        # 给明细赋单号
                        for item in sheet.items:
                            item.delivery_no = sheet.delivery_no
                        # 删除原单子
                        left_sheets.remove(sheet)
                        # 加入切分后剩余的新单子
                        left_sheets.insert(0, new_sheet)
                        # 原始单子列表加入新拆分出来的单子
                        sheets.append(new_sheet)
                    break


def split_sheet(sheet, limit_weight):
    """对超重的发货单进行分单"""
    total_weight = 0
    # 切分出的新单子
    new_sheet = copy.copy(sheet)
    # 原单子最终的明细
    sheet_items = []
    # 新单子的明细
    new_sheet_items = copy.copy(sheet.items)
    for item in sheet.items:
        # 计算发货单中的哪一子项超重
        total_weight += item.weight
        if total_weight <= limit_weight:
            # 原单子追加明细
            sheet_items.append(item)
            # 新单子减少明细
            new_sheet_items.remove(item)
        else:
            # 子单总重超过限制时分单
            item, new_item = weight_rule.split_item(item, total_weight - limit_weight)
            if new_item:
                # 原单子追加明细
                sheet_items.append(item)
                # 新单子减少明细
                new_sheet_items.remove(item)
                # 新单子加入新切分出来的明细
                new_sheet_items.insert(0, new_item)
            break
    if sheet_items:
        # 新单子单号
        # new_sheet.delivery_no = '提货单' + str(new_sheet_no)
        # 原单子明细重新赋值
        sheet.items = sheet_items
        sheet.weight = sum([i.weight for i in sheet.items])
        # 新单子明细赋值
        new_sheet.items = new_sheet_items
        new_sheet.weight = sum([i.weight for i in new_sheet.items])
        return sheet, new_sheet
    else:
        return sheet, None


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
    for sheet_group in load_task_dict.values():
        product_dict = {}
        for current in sheet_group:
            # 取出当前组内的发货单，根据发货单中第一个子单的品类映射到product_dict上，每个品类对应的发货单作为合并的母体
            product_type = product_type_rule.get_product_type(current.items[0])
            if not product_dict.__contains__(product_type):
                product_dict[product_type] = current
            else:
                source = product_dict[product_type]
                # 先将current的所有子单合并到source中，然后从sheets中删除被合并的发货单
                source.items.extend(current.items)
                source.weight += current.weight
                source.total_pcs += current.total_pcs
                sheets.remove(current)
                # 再判断物资代码是否相同，如果相同则认为同一种产品，将子单合并
                item_id_dict = {}
                for citem in copy.copy(source.items):
                    if not item_id_dict.__contains__(citem.item_id):
                        item_id_dict[citem.item_id] = citem
                    else:
                        sitem = item_id_dict[citem.item_id]
                        sitem.quantity += citem.quantity
                        sitem.free_pcs += citem.free_pcs
                        sitem.total_pcs +=citem.total_pcs
                        sitem.weight += citem.weight
                        source.items.remove(citem)


def print_sheets(sheets):
    """输出发货单摘要"""
    prt = [(s.delivery_no, s.weight) for s in sheets]
    print(prt)