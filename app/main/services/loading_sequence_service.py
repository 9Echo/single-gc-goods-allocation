from app.main.entity.delivery_sheet import DeliverySheet
from model_config import ModelConfig
import json
import math

"""
车型：13米，车宽2.4米，车厢高1.5米
1.确定摆放顺序，（将大、小管分类）
2.获取打包参数，确定摆放位置：[第几层，放什么，放几件，放几根，层高，本层剩余宽度]
"""


def loading():
    # 读取所有数据
    with open("result.json", "rt", encoding='utf-8') as f:
        temp = json.loads(f.read())
    # 得到所需的数据
    sheets = temp["data"]
    # 存放每一个发货单所装货物的列表
    load_list = []
    # 将货物按照load_task_id进行分类
    load_dict = {}
    # 下面将每个发货单上的货整理成一个列表添加到load_list中
    # 遍历每一个订单
    for sheet in sheets:
        if sheet["load_task_id"] not in load_dict:
            load_dict[sheet["load_task_id"]] = []
        # 通过sheet生成一个发货单对象
        de_sheet = DeliverySheet(sheet)
        # 遍历发货单中的每一个子单，整理子单信息添加到load_list中
        for item in de_sheet.items:
            # 分割 物资代码 得到外径：od_id
            od_id = item['item_id'].split("*")[0][3:].lstrip("0")
            # 为焊管 则查成件的高和宽
            if item["product_type"] == "焊管":
                # 通过外径查询焊管成捆后的高和宽：size ，example：360*370
                size = ModelConfig.HANGUAN_PACK_SIZE[od_id]
            # 此处暂且只考虑  焊管和热镀
            else:
                # 通过外径查询热镀成捆后的高和宽：size ，example：360*370
                size = ModelConfig.REDU_PACK_SIZE[od_id]
            # 判断所画图形的形状
            if item["product_type"] in ["焊管", "热镀"]:
                shape = "六边形"
            elif item["product_type"] == "方矩管":
                shape = "矩形"
            elif item["product_type"] == "螺旋焊管":
                shape = "圆形"
            # 将子单信息按【品名，件尺寸，规格，件数，散根数，总根数, 外径，形状】的格式添加到load_list中
            load_dict[sheet["load_task_id"]].append([item['product_type'],
                                                     size,
                                                     item['item_id'],
                                                     item['quantity'],
                                                     item['free_pcs'],
                                                     item['total_pcs'],
                                                     float(od_id),
                                                     shape])
    # 将每个订单的所有子单按照已录信息的外径从小到大排序
    for key in load_dict:
        load_dict[key].sort(key=lambda x: x[6])
        # 将该发货单中所装货物添加到load_list中
        load_list.append(load_dict[key])

    # 车型 车长， 车宽， 侧栏高
    car = [12000, 2400, 1500]
    # 装车清单
    box = []
    # items为一个发货单
    for items in load_list:
        # 存放所装的货物
        box_list = {}
        # item为发货单中的每一种货物
        for item in items:
            # 摆放货物
            box_list = put_goods(box_list, item)
        # 装车内外总高度
        total_height_out = 0
        total_height_in = 0
        # 计算装车内外的总高度
        for k in box_list:
            total_height_out += box_list[k]["height_out"]
            total_height_in += box_list[k]["height_in"]
        # 将每个一辆车上的货物清单和车内外车高都添加到box中
        box.append([box_list, total_height_in, total_height_out])

    return box


def put_goods(box_list, item):
    """
    根据传入的item摆放货物
    :param box_list: 车辆的装载情况字典 {"1":{l_width_in:??,l_width_out:??,height_in:??,height_out:??,goods_in:[??]，goods_out:[??]}, "2":...}
    :param item: 货物  [品名，尺寸，物资代码，件数，散根，总根数，外径，成件的截面形状]
    :return:
    """
    # 货物的高
    item_height = float(item[1].split("*")[0])
    # 货物的宽
    item_width = float(item[1].split("*")[1])
    # 得到当前的层数
    n = len(box_list)
    # 判断box_list是否为空
    if n != 0:
        # 遍历每一层
        for i in range(1, n+1):
            # 得到这一层里面的剩余宽度
            l_width_in = float(box_list[i]["l_width_in"])
            # 得到这一层外面的剩余宽度
            l_width_out = float(box_list[i]["l_width_out"])
            # 得到这一层里面的高度
            height_in = float(box_list[i]["height_in"])
            # 得到这一层外面的高度
            height_out = float(box_list[i]["height_out"])
            # 判断空间是否足够放下该item
            overspread(item_height, item_width, height_in, l_width_in, item, box_list, "l_width_in", i)
            overspread(item_height, item_width, height_out, l_width_out, item, box_list, "l_width_out", i)
        # 已有层都已经摆放过后 ， 继续向新一层摆放
        while item[3]:
            n += 1
            new_floor(box_list, item_width, item_height, item, n)
    else:
        while item[3]:
            n += 1
            new_floor(box_list, item_width, item_height, item, n)
    return box_list


def overspread(item_height, item_width, height, l_width, item, box_list, l_width_io, p):
    """
    将传入的item摆放在剩余的的宽度
    :param item_height: 待摆放货物的高
    :param item_width: 待摆放货物的宽
    :param height: 该层的货物高度
    :param l_width: 该层剩余宽度
    :param item: 待放货物 type: list
    :param box_list: 车层清单 type: dict
    :param l_width_io: l_width_in/l_width_out , 用来区别内外两层
    :param p: 车层
    :return:
    """
    # 只要剩余宽度比待放货物的高和宽任意一个大，就算是能放得下
    if item_height < l_width or item_width < l_width:
        # 该层剩余空间可放该item的件数 和 每件的宽度,  比较横着放和竖着放，选取放入数量多的那一种
        can_put_quantity, width, height_new = (math.floor(l_width / item_width), item_width, item_height) if math.floor(
            l_width / item_width) > math.floor(l_width / item_height) else (
        math.floor(l_width / item_height), item_height, item_width)
        # 复制一个货物信息，用来添加到该层所装的货物信息中
        put_item = item.copy()
        # 将散根数和总根数都置0
        put_item[4] = 0
        put_item[5] = 0
        # 如果可放件数小于货物总数，则放入件数为可放件数
        if can_put_quantity < item[3]:
            # 修改在该层中放的件数
            put_item[3] = can_put_quantity
            # 扣去摆放的件数， 得到剩余的件数
            item[3] -= can_put_quantity
        # 否则为 货物总数，且修改货物总数为0
        else:
            can_put_quantity = item[3]
            put_item[3] = item[3]
            item[3] = 0
        # 更新该层的剩余宽度，此处对单层进行分析，所以摆放数量不必除以二
        box_list[p][l_width_io] = float(l_width) - float(width) * float(can_put_quantity)
        # 区分内外层添加所装货物
        if l_width_io == "l_width_in":
            goods_io = "goods_in"
            height_io = "height_in"
        else:
            goods_io = "goods_out"
            height_io = "height_out"
        # 添加该层的货物
        box_list[p][goods_io].append(put_item)
        # 更新层高
        if height < height_new:
            box_list[p][height_io] = height_new


def new_floor(box_list, item_width, item_height, item, n):
    """
    添加新的一层，摆放货物
    :param box_list: 车层清单 type:dict
    :param item_width:货物宽度
    :param item_height:货物高度
    :param item:货物信息 type:list
    :param n:新的一层  层数
    :return:
    """
    # 构建新一层
    box_list[n] = {"l_width_in": 2400, "l_width_out": 2400, "height_in": 0, "height_out": 0, "goods_in": [], "goods_out": []}
    # 得到该层可摆放的件数
    next_floor_can_put_quantity = math.floor(box_list[n]["l_width_in"] / item_width) * 2
    # 拷贝货物信息
    next_floor_put_item1 = item.copy()
    next_floor_put_item2 = item.copy()
    if next_floor_can_put_quantity < item[3]:
        # 扣去摆放的件数，得到剩余的件数
        item[3] -= next_floor_can_put_quantity
    # 否则为货物总数，且修改货物总数为0
    else:
        next_floor_can_put_quantity = item[3]
        item[3] = 0
    # 判断摆放的货物件数是否为偶数， 为偶数则内外层摆放数量一致，否则内层多摆
    if next_floor_can_put_quantity % 2 != 0:
        q = next_floor_can_put_quantity // 2
        m = q + 1
    else:
        q = m = next_floor_can_put_quantity / 2
    # 修改放在该层的货物信息
    if q != 0:
        next_floor_put_item1[3] = q
        next_floor_put_item1[4] = 0
        next_floor_put_item1[5] = 0
        box_list[n]["l_width_out"] -= q * item_width
        box_list[n]["height_out"] = item_height
        box_list[n]["goods_out"].append(next_floor_put_item1)
    next_floor_put_item2[3] = m
    next_floor_put_item2[4] = 0
    next_floor_put_item2[5] = 0
    box_list[n]["l_width_in"] -= m * item_width
    box_list[n]["height_in"] = item_height
    box_list[n]["goods_in"].append(next_floor_put_item2)


if __name__ == '__main__':
    result = loading()
    for i in result:
        print(i)
