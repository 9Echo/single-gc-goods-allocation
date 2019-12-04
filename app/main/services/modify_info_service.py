# coding=utf-8
# create:chengtao 2019.12.4
# description: 整理库存需要扣除的规格的数量
import json


def modify_info(deliveries=[]):
    info = {}
    if not len(deliveries):
        pass
    else:
        for delivery in deliveries:
            # # 得发货通知单号
            # delivery_no = delivery.delivery_no
            # # 返货通知单的总件数
            # delivery_total_quantity = delivery.delivery_quantity
            for item in delivery.items:
                # 产品代码
                item_id = item.id
                # 产品总件数
                item_quantity = item.quantity
                # 产品散根数
                item_free_pcs = item.free_pcs
                # 将产品规格作为键 添加散根和总件
                if item_id not in info:
                    info[item_id] = {}
                info[item_id]["item_quantity"] = info[item_id].get("item_quantity", 0.0) + float(item_quantity)
                info[item_id]["item_free_pcs"] = info[item_id].get("item_free_pcs", 0.0) + float(item_free_pcs)
    return json.dumps(info)

