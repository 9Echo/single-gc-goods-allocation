
import copy

from flask import g

from app.main.pipe_factory.rule import weight_rule
from model_config import ModelConfig



def dispatch_load_task_optimize(sheets: list, task_id):
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
                sheet, new_sheet = split_sheet_optimize(sheet, limit_weight)
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
                        sheet, new_sheet = split_sheet_optimize(sheet, limit_weight)
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

def dispatch_load_task_spec(sheets: list, task_id):
    """
    将发货单根据重量组合到对应的车次上
    :param sheets:
    :param task_id:
    :return:
    """

    doc_type = '提货单'
    left_sheets = []
    for sheet in sheets:
        # 如果已经生成车次的sheet，则跳过不处理
        if sheet.load_task_id:
            continue
        else:
            left_sheets.append(sheet)
    # 记录是否有未分车的单子
    while left_sheets:
        total_weight = 0
        total_volume = 0
        task_id += 1
        no = 0
        # 下差组别的总重量
        rd_lx_total_weight = 0
        for sheet in copy.copy(left_sheets):
            total_weight += sheet.weight
            total_volume += sheet.volume
            # 初始重量
            new_max_weight = g.MAX_WEIGHT
            # 如果是下差过大的品种，重量累加
            if sheet.items and sheet.items[0].product_type in ModelConfig.RD_LX_GROUP:
                rd_lx_total_weight += sheet.weight
            # 如果该车次有下差过大的品种，动态计算重量上限
            if rd_lx_total_weight:
                # 新最大载重上调 下差组别总重量/热镀螺旋最大载重 * 1000
                new_max_weight = round(
                    g.MAX_WEIGHT + (rd_lx_total_weight / g.RD_LX_MAX_WEIGHT) * g.RD_LX_UP_WEIGHT)
                new_max_weight = min(g.RD_LX_MAX_WEIGHT, new_max_weight)
            # 如果当前车次总体积占比超出，计算剩余体积比例进行重量切单
            if total_volume > ModelConfig.MAX_VOLUME:
                # 按照体积比例计算，在最新的最大重量限制下还可以放多少重量
                limit_volume_weight = (ModelConfig.MAX_VOLUME - total_volume + sheet.volume) / sheet.volume * sheet.weight
                # 在最新的最大重量限制下还可以放多少重量
                limit_weight_weight = new_max_weight - (total_weight - sheet.weight)
                # 取较小的
                limit_weight = min(limit_weight_weight, limit_volume_weight)
                sheet, new_sheet = split_sheet_spec(sheet, limit_weight)
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
                if total_weight <= new_max_weight:
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
                    if new_max_weight - total_weight < ModelConfig.TRUCK_SPLIT_RANGE:
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
                        limit_weight = new_max_weight - (total_weight - sheet.weight)
                        sheet, new_sheet = split_sheet_spec(sheet, limit_weight)
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


def split_sheet_spec(sheet, limit_weight):
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
            item, new_item = weight_rule.split_item_spec(item, total_weight - limit_weight)
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

def split_sheet_optimize(sheet, limit_weight):
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
            item, new_item = weight_rule.split_item_optimize(item, total_weight - limit_weight)
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

