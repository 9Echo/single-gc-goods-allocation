from app.main.entity.delivery_sheet import DeliverySheet
from model_config import ModelConfig
import json

"""
车型：13米，车宽2.4米，车厢高1.5米
1.确定摆放顺序，（将大、小管分类）
2.获取打包参数，确定摆放位置：[第几层，放什么，放几件，放几根，层高，本层剩余宽度]
"""


def loading():
    # 读数据
    with open("result.json", "rt", encoding='utf-8') as f:
        temp = json.loads(f.read())
    sheets = temp["data"]
    load_list = []
    for sheet in sheets:
        de_sheet = DeliverySheet(sheet)
        for item in de_sheet.items:
            od_id = item['item_id'].split("*")[0][-2:]
            size = ModelConfig.hanguan_pack_size[od_id]
            # 品名，件尺寸，规格，件数，散根数，总根数
            load_list.append([item['product_type'], size, item['item_id'], item['quantity'], item['free_pcs'], item['total_pcs']])
    # 将货物按直径排成从小管-->大管的顺序
    load_list = sorted(load_list, key=(lambda x: x[1]))

    # 车型
    car = [12000, 2400, 1500]
    car_w = int(car[1])

    # 装货过程
    box_list = []
    i = 0
    l_width = car_w
    for item in load_list:
        # 获取单件尺寸
        print(item)
        l_quantity = None
        floors = []
        while l_quantity != 0:
            box = {'floor': 0,
                   'item': []}
            box, l_quantity, l_width = load_the_floor(box, i, item, l_width)
            # 整理数据，将每层的放到一个字典里面
            for load_item in box_list:
                if load_item["floor"] not in floors:
                    floors.append(load_item["floor"])
            if box["floor"] in floors:
                for load_item in box_list:
                    if box["floor"] == load_item["floor"]:
                        load_item["item"].append(box["item"][0])
            else:
                box_list.append(box)
            item[3] = l_quantity
            l_i = int(item[1].split('*')[1])
            # 如果本层剩余宽度小于件宽，换下一层
            if l_width < l_i:
                l_width = car_w
                i = i + 1

    # 求装车总高度
    total_height = 0
    for i in box_list:
        max_height = i["item"][0]["height"]
        for j in i["item"]:
            if j["height"] > max_height:
                max_height = j["height"]
        total_height = total_height + max_height
    return total_height, box_list


def load_the_floor(box, i, load, l_width):
    """
    这层不能放下这一种，那就放它能放下的
    :param box:盒子
    :param i:层数
    :param load:货物信息
    :param l_width:本层的剩余宽度
    :return: 返回这一层的货物信息和剩余未放置件数
    """
    size_list = load[1].split('*')
    l_i = int(size_list[0])
    w_i = int(size_list[1])

    length = int(load[2].split('*')[2])
    if length > 6500:
        n = int(l_width / l_i)  # 一层可以放多少件
    elif length == 6000:
        n = int(l_width / l_i) * 2  # 一层可以放多少件

    # 盒子里放的货物
    item = {'product_type': 0,
            'size':None,
             'item_id': None,
             'quantity': 0,
            'free_pcs': 0,
            'height': 0,
            'l_width': 0}
    # 这一层不能放下
    if n < load[3]:
        box['floor'] = i + 1
        item['product_type'] = load[0]
        item['size'] = load[1]
        item['item_id'] = load[2]
        item['quantity'] = n
        item['free_pcs'] = 0
        item['height'] = w_i
        item['l_width'] = l_width - n / 2 * l_i
        print(item)
        box['item'].append(item)
        l_quantity = load[3] - n
        return box, l_quantity, item['l_width']
    # 这一层可以放下
    elif n >= load[3]:
        box['floor'] = i + 1
        item['product_type'] = load[0]
        item['size'] = load[1]
        item['item_id'] = load[2]
        item['quantity'] = load[3]
        item['free_pcs'] = load[4]
        item['height'] = w_i
        item['l_width'] = l_width - load[3] / 2 * l_i
        print(item)
        box['item'].append(item)
        return box, 0, item['l_width']


if __name__ == '__main__':
    total_height, result_list = loading()
    print(total_height, result_list)
