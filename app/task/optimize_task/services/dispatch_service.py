# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:20
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13
import copy
import math
from threading import Thread
from app.main.pipe_factory.entity.delivery_item import DeliveryItem
from app.main.pipe_factory.entity.delivery_sheet import DeliverySheet
from app.main.pipe_factory.service import redis_service
from app.main.pipe_factory.service.create_delivery_item_service import CreateDeliveryItem
from app.main.pipe_factory.service.replenish_property_service import replenish_property
from app.task.optimize_task.analysis.rules import dispatch_filter, product_type_rule, weight_rule
from app.util import weight_calculator
from app.util.uuid_util import UUIDUtil
from model_config import ModelConfig
import pandas as pd
from flask import g


def dispatch(order):
    """根据订单执行分货
    """
    # 1、将订单项转为发货通知单子单的list
    delivery_item_list = CreateDeliveryItem(order)
    # delivery_item_list.is_success=False证明有计算异常,返回一张含有计算出错子项的sheet
    if not delivery_item_list.success:
        return delivery_item_list.failsheet()
    else:
        # 调用optimize()，即将大小管分开
        max_delivery_items, min_delivery_items = delivery_item_list.optimize()

    if max_delivery_items:
        # 2、使用模型过滤器生成发货通知单

        sheets = []
        task_id=0
        sheets, task_id = dispatch_filter.filter(max_delivery_items)
        # 3、补充发货单的属性
        batch_no = UUIDUtil.create_id("ba") #batch_no 在后面的装车需要
        replenish_property(sheets, order, batch_no)
        # 为发货单分配车次

        task_id = dispatch_load_task(sheets, task_id)
    if min_delivery_items:
        # 小管装填大管车次
        load_task_fill(sheets, min_delivery_items, task_id, order, batch_no)
    # 车次提货单合并
    combine_sheets(sheets)
    sheets.sort(key=lambda i: i.load_task_id)
    # 6、将推荐发货通知单暂存redis
    Thread(target=redis_service.set_delivery_list, args=(sheets,)).start()
    return sheets


def dispatch_load_task(sheets: list, task_id):
    """将发货单根据重量组合到对应的车次上"""

    doc_type = '提货单'
    left_sheets = []
    # 先为重量为空或已满的单子生成单独车次
    for sheet in sheets:
        # 如果已经生成车次的sheet，则跳过不处理
        if sheet.load_task_id:
            continue
        max_weight = 0
        if sheet.items and sheet.items[0].product_type in ModelConfig.RD_LX_GROUP:
            max_weight = g.RD_LX_MAX_WEIGHT
        if sheet.weight == 0 or sheet.weight >= (max_weight or g.MAX_WEIGHT):
            task_id += 1
            sheet.load_task_id = task_id
        else:
            left_sheets.append(sheet)
    # 记录是否有未分车的单子
    while left_sheets:
        total_weight = 0
        total_volume = 0
        task_id += 1
        no = 0
        # 动态计算的车次总重量
        new_max_weight = 0
        # 下差组别的总重量
        rd_lx_total_weight = 0
        for sheet in copy.copy(left_sheets):
            total_weight += sheet.weight
            total_volume += sheet.volume
            # 如果是下差过大的品种，重量累加
            if sheet.items and sheet.items[0].product_type in ModelConfig.RD_LX_GROUP:
                rd_lx_total_weight += sheet.weight
            # 如果有下差过大的品种，动态计算重量上限
            if rd_lx_total_weight:
                # 新最大载重上调 下差组别总重量/热镀螺旋最大载重 * 1000
                new_max_weight = round(
                    g.MAX_WEIGHT + (rd_lx_total_weight / g.RD_LX_MAX_WEIGHT) * 1000)
                new_max_weight = g.RD_LX_MAX_WEIGHT if new_max_weight > g.RD_LX_MAX_WEIGHT else new_max_weight

            # 如果当前车次总体积占比超出，计算剩余体积比例进行重量切单
            if total_volume > ModelConfig.MAX_VOLUME:
                limit_weight_volume = (
                                              ModelConfig.MAX_VOLUME - total_volume + sheet.volume) / sheet.volume * sheet.weight
                limit_weight_weight = (new_max_weight or g.MAX_WEIGHT) - (total_weight - sheet.weight)
                limit_weight = limit_weight_weight if limit_weight_volume > limit_weight_weight else limit_weight_volume
                sheet, new_sheet = split_sheet(sheet, limit_weight)
                if new_sheet:
                    # 分单成功时旧单放入当前车上，新单放入等待列表
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
            # 体积不超，处理重量
            else:
                # 如果总重量小于最大载重
                if total_weight <= (new_max_weight or g.MAX_WEIGHT):
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
                    if (new_max_weight or g.MAX_WEIGHT) - total_weight < ModelConfig.TRUCK_SPLIT_RANGE:
                        # 接近每车临界值时停止本次装车
                        break
                # 如果超重
                else:
                    # 超重时对发货单进行分单
                    if sheet.weight < ModelConfig.TRUCK_SPLIT_RANGE:
                        # 重量不超过1吨（可配置）的发货单不分单
                        break
                    # 如果大于1吨
                    else:
                        # 对满足条件的发货单进行分单
                        limit_weight = (new_max_weight or g.MAX_WEIGHT) - (total_weight - sheet.weight)
                        sheet, new_sheet = split_sheet(sheet, limit_weight)
                        if new_sheet:
                            # 分单成功时旧单放入当前车上，新单放入等待列表
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
    return task_id


def split_sheet(sheet, limit_weight):
    """
    对超重的发货单进行分单
    limit_weight：当前车次重量剩余载重
    total_volume：当前车次目前体积占比
    """
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
        #  如果当前车次超重
        else:
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
        # 原单子明细重新赋值
        sheet.items = sheet_items
        sheet.weight = sum([i.weight for i in sheet.items])
        sheet.total_pcs = sum([i.total_pcs for i in sheet.items])
        sheet.volume = sum([i.volume for i in sheet.items])
        # 新单子明细赋值
        new_sheet.items = new_sheet_items
        new_sheet.weight = sum([i.weight for i in new_sheet.items])
        new_sheet.total_pcs = sum([i.total_pcs for i in new_sheet.items])
        new_sheet.volume = sum([i.volume for i in new_sheet.items])
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
            # 如果发现重量为0的明细，移除
            for citem in copy.copy(source.items):
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


def sort_by_weight(sheets):
    sheets_dict = [sheet.as_dict() for sheet in sheets]
    new_sheets = []
    if sheets_dict:
        df = pd.DataFrame(sheets_dict)
        series = df.groupby(by=['load_task_id'])['weight'].sum().sort_values(ascending=False)
        task_id = 0
        for k, v in series.items():
            task_id += 1
            doc_type = '提货单'
            no = 0
            current_sheets = list(filter(lambda i: i.load_task_id == k, sheets))
            for sheet in current_sheets:
                no += 1
                sheet.load_task_id = task_id
                sheet.delivery_no = doc_type + str(task_id) + '-' + str(no)
                for item in sheet.items: item.delivery_no = sheet.delivery_no
                new_sheets.append(sheet)
                sheets.remove(sheet)
    return new_sheets


def load_task_fill(sheets, min_delivery_item, task_id, order, batch_no):
    """
    小管装填大管车次，将小管按照件数从小到大排序
    若小管不够，分完结束
    若小管装填完所有车次后有剩余，进行背包和遍历
    :param batch_no: 分货批次号
    :param order: 订单
    :param sheets:大管的提货单列表
    :param min_delivery_item:小管的子项列表
    :param task_id:当前分配车次号
    :return: None
    """
    if not sheets:
        # 2、使用模型过滤器生成发货通知单
        min_sheets, task_id = dispatch_filter.filter(min_delivery_item)
        # 3、补充发货单的属性
        replenish_property(sheets, order, batch_no)
        # 为发货单分配车次
        dispatch_load_task(min_sheets, task_id)
        sheets.extend(min_sheets)
    else:
        min_delivery_item.sort(key=lambda i: i.quantity)
        sheets_dict = [sheet.as_dict() for sheet in sheets]
        df = pd.DataFrame(sheets_dict)
        series = df.groupby(by=['load_task_id'])['weight'].sum().sort_values(ascending=False)
        for k, v in series.items():
            max_weight = 0
            current_weight = v
            # 判断该车次是否下差过大
            current_sheets = list(filter(lambda i: i.load_task_id == k, sheets))
            if current_sheets and current_sheets[0].items:
                if current_sheets[0].items[0].product_type in ModelConfig.RD_LX_GROUP:
                    max_weight = g.RD_LX_MAX_WEIGHT
            if v >= (max_weight or g.MAX_WEIGHT):
                continue
            for i in copy.copy(min_delivery_item):
                # 如果该子项可完整放入
                if i.weight <= (max_weight or g.MAX_WEIGHT) - current_weight:
                    # 当前重量累加
                    current_weight += i.weight
                    # 生成新提货单，归到该车次下
                    new_sheet = DeliverySheet()
                    new_sheet.load_task_id = k
                    new_sheet.volume = i.volume
                    new_sheet.batch_no = batch_no
                    new_sheet.customer_id = order.customer_id
                    new_sheet.salesman_id = order.salesman_id
                    new_sheet.weight = i.weight
                    new_sheet.total_pcs = i.total_pcs
                    new_sheet.type = 'recommend_first'
                    new_sheet.items.append(i)
                    sheets.append(new_sheet)
                    # 移除掉被分配的子项
                    min_delivery_item.remove(i)
                else:
                    i, new_item = \
                        weight_rule.split_item(i, i.weight - ((max_weight or g.MAX_WEIGHT) - current_weight))
                    if new_item:
                        # 生成新提货单，归到该车次下
                        new_sheet = DeliverySheet()
                        new_sheet.load_task_id = k
                        new_sheet.volume = i.volume
                        new_sheet.batch_no = batch_no
                        new_sheet.customer_id = order.customer_id
                        new_sheet.salesman_id = order.salesman_id
                        new_sheet.weight = i.weight
                        new_sheet.type = 'recommend_first'
                        new_sheet.total_pcs = i.total_pcs
                        new_sheet.items.append(i)
                        # 移除掉被分配的子项
                        min_delivery_item.remove(i)
                        # 将剩余的子项放入子项列表
                        min_delivery_item.insert(0, new_item)
                        sheets.append(new_sheet)
                    break
        # 装填完如果小管还有剩余，进行单独分货
        if min_delivery_item:
            # 2、使用模型过滤器生成发货通知单
            min_sheets, task_id = dispatch_filter.filter(min_delivery_item, task_id)
            # 3、补充发货单的属性
            for sheet in min_sheets:
                sheet.batch_no = batch_no
                sheet.customer_id = order.customer_id
                sheet.salesman_id = order.salesman_id
                sheet.weight = 0
                sheet.total_pcs = 0
                for di in sheet.items:
                    di.delivery_item_no = UUIDUtil.create_id("di")
                    sheet.weight += di.weight
                    sheet.total_pcs += di.total_pcs
            # 为发货单分配车次
            dispatch_load_task(min_sheets, task_id)
            sheets.extend(min_sheets)


def create_sheet_item(order):
    max_delivery_items = []
    min_delivery_items = []

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
        di.max_quantity = ModelConfig.ITEM_ID_DICT.get(di.item_id[:3])
        di.volume = di.quantity / di.max_quantity if di.max_quantity else 0 #在配置文件里找不到最大数据的视为小管
        di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)
        di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)
        # 如果遇到计算不出来的明细，返回0停止计算
        if di.weight == 0:
            return [di], [], False
        # 搜集小管
        if di.volume == 0:
            min_delivery_items.append(di)
            continue
        # 如果该明细有件数上限并且单规格件数超出，进行切单
        if di.max_quantity and di.quantity > di.max_quantity:
            # copy次数
            count = math.floor(di.quantity / di.max_quantity)
            # 最后一个件数余量
            surplus = di.quantity % di.max_quantity
            # 标准件数的重量和总根数
            new_weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.max_quantity, 0)
            new_total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.max_quantity, 0)
            # 创建出count个拷贝的新明细，散根数为0，件数为标准件数，总根数为标准总根数，体积占比近似为1
            for i in range(0, count):
                copy_di = copy.deepcopy(di)
                copy_di.free_pcs = 0
                copy_di.quantity = di.max_quantity
                copy_di.volume = 1
                copy_di.weight = new_weight
                copy_di.total_pcs = new_total_pcs
                # 将新明细放入明细列表
                max_delivery_items.append(copy_di)
            # 原明细更新件数为剩余件数，体积占比通过件数/标准件数计算
            di.quantity = surplus
            di.volume = di.quantity / di.max_quantity if di.max_quantity else 0
            di.weight = weight_calculator.calculate_weight(di.product_type, di.item_id, di.quantity, di.free_pcs)
            di.total_pcs = weight_calculator.calculate_pcs(di.product_type, di.item_id, di.quantity, di.free_pcs)

        max_delivery_items.append(di)
    return max_delivery_items, min_delivery_items, True

