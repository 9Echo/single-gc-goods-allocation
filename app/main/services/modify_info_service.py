# coding=utf-8
# create:chengtao 2019.12.4
# description: 整理库存需要扣除的规格的数量及返回管厂的json数据
import json
import requests

from app.utils.result import Result


def get_data(delivery=[]):
    if not delivery:
        return Result.error("未传入数据或传入数据为空！").msg
    data_info = modify_info(delivery)
    data_result = trans_format(delivery)
    data_result["data_info"] = data_info
    # return json.dumps(data_result)
    return Result.success_response(None)


def modify_info(deliveries):
    data_info = {}
    for delivery in deliveries:
        for item in delivery.items:
            # 产品代码
            item_id = item.id
            # 产品总件数
            item_quantity = item.quantity
            # 产品散根数
            item_free_pcs = item.free_pcs
            # 将产品规格作为键 添加散根和总件
            if item_id not in data_info:
                data_info[item_id] = {}
            data_info[item_id]["item_quantity"] = data_info[item_id].get("item_quantity", 0.0) + float(item_quantity)
            data_info[item_id]["item_free_pcs"] = data_info[item_id].get("item_free_pcs", 0.0) + float(item_free_pcs)
    return data_info


def trans_format(deliveries):
    """生成管厂所需的数据格式(发货通知单-主、子单)

    Args:
        deliveries: 生成的发货通知单

    Returns:
        dic:    符合管厂格式的通知单

    Raise:

    """
    data_result = {"data": []}
    for delivery in deliveries:
        temp = {
            "CORPID": "HL",  # HL
            "I_O": "O",  # 出入库标记
            "DOCTYPE": "",  # 录入人ID-前端传入
            "DOCUNO": "",  # ??未解决 提货单号-前端传入
            "ORG_UNIT": "",  # 客户公司简称-1.前端2.通过订单号订单表查出
            "TRX_DATE": delivery.create_time.split(" ")[0],  # CRTED_DATE 的年月日
            "TRX_QTY": "0.00",  # 0.00
            "TRX_AMT": "0.00",  # 0.00
            "TRX_ZGOO": "",  # ??数字
            "LRR": "",  # 录入人即开单员名字首字母-前端传入
            "BBR": " ",  # 空着
            "SALESORG": "",  # 销售部门ID-前端传入
            "SLSMAN": "",  # 销售员ID-前端传入
            "CRTED_DATE": delivery.create_time,  # 创建时间
            "UPTED_DATE": delivery.update_time,  # 更新时间
            "UPTED_by": "",  # LRR
            "F_WHS": delivery.items[0].warehouse,  # 仓库
            "F_LOC": delivery.items[0].loc_id,  # 垛号
            "TRX_J": "0",  # 0
            "TRX_G": "0",  # 0
            "ORDER_J": delivery.total_quantity,  # 总件数
            "ORDER_G": delivery.free_pcs,  # 散根数
            "ORDER_ZGOO": deliveries.total_pcs,  # 总根数
            "ORDER_TWE": "",  # ??数字
            "ORDER_AMT": "",  # ??数字
            "FEE_ORDER": "0.00",  # 0.00
            "NOTE": " ",  # 空着
            "PDBZ": "空",  # ‘空’
            "DIBZ": "N",  # N
            "JSDOCUNO": "",  # ??例如：1908-x4-00320
            "YWLX": "",  # ??1
            "ORDER_CAL": delivery.weight,  # 理重
            "THFS": "",  # ??
            "items": []
        }
        for item in delivery.items:
            temp2 = {
                        "CORPID": "HL",  # HL
                        "I_O": "O",  # 出入库标记
                        "DOCTYPE": "",  # 录入人ID-前端传入
                        "DOCUNO": "",  # 提货单号-前端传入
                        "LNO": "",  # ??数字
                        "ORG_UNIT": "",  # 客户公司简称-前端传入
                        "TRX_DATE": item.create_time.split(" ")[0],  # CRTED_DATE 取年月日
                        "ITEMID": item.item_id,  # 物资代码item_id
                        "GHOO": item.ghoo,  # 材质
                        "LOT_NO": "n",  # n
                        "UOM_ID": "kg",  # 单位kg
                        "TRX_QTY": " ",  # 空着
                        "PRC_IN": "",  # ??数字
                        "AMT_IN": "",  # ??数字300只有一个
                        "BZDM": " ",  # 空着
                        "JZDM": " ",  # 空着
                        "BZRS": " ",  # 空着
                        "GSS": " ",  # 空着
                        "S_DATE": " ",  # 空着
                        "E_DATE": " ",  # 空着
                        "LRR": "",  # 录入人首字母-前端传入
                        "BRR": " ",  # 空着
                        "SALESORG": "",  # 销售部门-前端传入
                        "SLSMAN": "",  # 销售员-前端传入
                        "CRTED_DATE": item.create_time,  # 创建时间 create_time
                        "UPTED_DATE": item.create_time,  # 更新时间 等于create_time
                        "UPTED_by": "",  # LRR
                        "ENTER_J": item.quantity,  # 件数
                        "ENTER_G": item.free_pcs,  # 散根
                        "ZGOO": item.total_pcs,  # 总根数
                        "CATNO": "",  # 01、02...??
                        "SUBCLS": "",  # 数字或字母??
                        "BZOO": "",  # ??备注
                        "F_WHS": item.warehouse,  # 仓库 warehouse
                        "F_LOC": item.loc_id,  # 垛号 loc_id
                        "COSTPRC": " ",  # 空着
                        "ORDER_QTY": "",  # ??
                        "PDBZ": "空",  # 空
                        "DIBZ": "N",  # N
                        "JSDOCUNO": "",  # ??例如：1908-x3-00145
                        "YWLX": "",  # ??1或2
                        "AUTONO": "",  # ?? 例如：1257378
                        "ORDER_DW": "t",  # t 单位 吨
                        "UOMRATE": "1000.00",  # 1000.00 物料单位转换
                        "TRX_DW": " ",  # 空着
                        "VALIDZL": "1",  # 1
                        "ACNO": " ",  # 空着
                        "QUALITY": "n",  # n
                        "MAKER": "n",  # n
                        "RKRQ": "",  # ??
                        "ZLLEVEL": "n",  # n
                        "PACKAGESPEC": "",  # ??
                        "HTNO": "n",  # n
                        "CUSTNAME": "",  # ??
                        "DGWIDTH": "",  # ??
                        "DGHEIGHT": "",  # ??
                        "DGLENGTH": "",  # ??
                        "ORDER_J": item.quantity,  # 件数
                        "ORDER_G": item.free_pcs,  # 散根数
                        "ORDER_ZGOO": item.total_pcs,  # 总根数
                        "PRC_ORDER": "",  # ??
                        "FEE_ORDER": " ",  # 空着
                    }
            temp["items"].append(temp2)
        data_result["data"].append(temp)
    return data_result

    # dic = {
    #         "data": [{
    #                 "CORPID": "HL",      # HL
    #                 "I_O": "",         # 出入库标记
    #                 "DOCTYPE": "",     # 录入人ID-前端传入
    #                 "DOCUNO": "",      # ？？未解决 提货单号-前端传入
    #                 "ORG_UNIT": "",    # 客户公司简称-1.前端2.通过订单号订单表查出
    #                 "TRX_DATE": "",    # CRTED_DATE 的年月日
    #                 "TRX_QTY": "",     # 0.00
    #                 "TRX_AMT": "",     # 0.00
    #                 "TRX_ZGOO": "",    # ??数字
    #                 "LRR": "",         # 录入人即开单员名字首字母-前端传入
    #                 "BBR": "",         # 空着
    #                 "SALESORG": "",    # 销售部门ID-前端传入
    #                 "SLSMAN": "",      # 销售员ID-前端传入
    #                 "CRTED_DATE": "",  # 创建时间
    #                 "UPTED_DATE": "",  # 更新时间
    #                 "UPTED_by": "",    # LRR
    #                 "F_WHS": "",       # 仓库
    #                 "F_LOC": "",       # 垛号
    #                 "TRX_J": "",       # 0
    #                 "TRX_G": "",       # 0
    #                 "ORDER_J": "",     # 总件数
    #                 "ORDER_G": "",     # 散根数
    #                 "ORDER_ZGOO": "",  # 总根数
    #                 "ORDER_TWE": "",   # ??数字
    #                 "ORDER_AMT": "",   # ??数字
    #                 "FEE_ORDER": "",   # 0.00
    #                 "NOTE": "",        # 空着
    #                 "PDBZ": "",        # ‘空’
    #                 "DIBZ": "",        # N
    #                 "JSDOCUNO": "",    # ??例如：1908-x4-00320
    #                 "YWLX": "",        # ??1
    #                 "ORDER_CAL": "",   # 理重
    #                 "THFS": "",        # ??
    #                 "items": [{
    #                             "CORPID": "",      # HL
    #                             "I_O": "",         # 出入库标记
    #                             "DOCTYPE": "",     # 录入人ID-前端传入
    #                             "DOCUNO": "",      # 提货单号-前端传入
    #                             "LNO": "",         # ??数字
    #                             "ORG_UNIT": "",    # 客户公司简称-前端传入
    #                             "TRX_DATE": "",    # CRTED_DATE 取年月日
    #                             "ITEMID": "",      # 物资代码item_id
    #                             "GHOO": "",        # 材质
    #                             "LOT_NO": "",      # n
    #                             "UOM_ID": "",      # 单位kg
    #                             "TRX_QTY": "",     # 空着
    #                             "PRC_IN": "",      # ??数字
    #                             "AMT_IN": "",      # ??数字300只有一个
    #                             "BZDM": "",        # 空着
    #                             "JZDM": "",        # 空着
    #                             "BZRS": "",        # 空着
    #                             "GSS": "",         # 空着
    #                             "S_DATE": "",      # 空着
    #                             "E_DATE": "",      # 空着
    #                             "LRR": "",         # 录入人首字母-前端传入
    #                             "BRR": "",         # 空着
    #                             "SALESORG": "",    # 销售部门-前端传入
    #                             "SLSMAN": "",      # 销售员-前端传入
    #                             "CRTED_DATE": "",  # 创建时间 create_time
    #                             "UPTED_DATE": "",  # 更新时间 等于create_time
    #                             "UPTED_by": "",     # LRR
    #                             "ENTER_J": "",     # 件数
    #                             "ENTER_G": "",     # 散根
    #                             "ZGOO": "",        # 总根数
    #                             "CATNO": "",       # 01、02...??
    #                             "SUBCLS": "",      # 数字或字母??
    #                             "BZOO": "",        # ??备注
    #                             "F_WHS": "",       # 仓库 warehouse
    #                             "F_LOC": "",     # 垛号 loc_id
    #                             "COSTPRC": "",     # 空着
    #                             "ORDER_QTY": "",   # ??
    #                             "PDBZ": "",        # 空
    #                             "DIBZ": "",        # N
    #                             "JSDOCUNO": "",    # ??例如：1908-x3-00145
    #                             "YWLX": "",        # ??1或2
    #                             "AUTONO": "",      # ?? 例如：1257378
    #                             "ORDER_DW": "",    # t 单位 吨
    #                             "UOMRATE": "",     # 1000.00 物料单位转换
    #                             "TRX_DW": "",      # 空着
    #                             "VALIDZL": "",     # 1
    #                             "ACNO": "",        # 空着
    #                             "QUALITY": "",     # n
    #                             "MAKER": "",       # n
    #                             "RKRQ": "",        # ??
    #                             "ZLLEVEL": "",     # n
    #                             "PACKAGESPEC": "",   # ??
    #                             "HTNO": "",        # n
    #                             "CUSTNAME": "",    # ??
    #                             "DGWIDTH": "",     # ??
    #                             "DGHEIGHT": "",    # ??
    #                             "DGLENGTH": "",    # ??
    #                             "ORDER_J": "",     # 件数
    #                             "ORDER_G": "",     # 散根数
    #                             "ORDER_ZGOO": "",  # 总根数
    #                             "PRC_ORDER": "",   # ??
    #                             "FEE_ORDER": "",   # 空着
    #                             }]
    #                 }]
    #         }


def request_middle():
    """将符合管厂的数据dic、需要扣除的库存数据info发送给中间服务端

    Args:

    Returns:

    Raise:

    """
    pass


