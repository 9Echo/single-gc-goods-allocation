import pandas as pd
from typing import List
from app.main.entity.load_task import LoadTask
from app.utils.get_static_path import get_path


def generate_excel(load_task_list: List[LoadTask]):
    df = pd.DataFrame([item.as_dict() for item in load_task_list])
    writer = pd.ExcelWriter(get_path("分货结果.xlsx"))

    df=df[(df['load_task_id']>=1)]
    df1 = df.groupby(['city', 'end_point', 'big_commodity']).agg(
        {'weight': 'sum'}).reset_index()
    df2 = df.groupby(['city', 'end_point'])['load_task_id'].nunique().reset_index()
    load_list = []
    for index, row in df1.iterrows():
        temp_df = df2[(df2['city'] == row['city']) & (df2['end_point'] == row['end_point'])]

        load_list.append(list(temp_df['load_task_id'])[0])
    # 增加新的一列车次数
    df1['load_num'] = load_list

    df.rename(index=str,
               columns={
                   "load_task_id": "车次号",
                   "priority": "优先级",
                   "load_task_type": "装卸类型",
                   "total_weight": "总重量",
                   "weight": "重量",
                   "count": "件数",
                   "city": "城市",
                   "end_point": "区县",
                   "big_commodity": "大品种",
                   "commodity": "小品种",
                   "notice_num": "发货通知单号",
                   "oritem_num": "订单号",
                   "standard": "规格",
                   "sgsign": "材质",
                   "outstock_code": "出库仓库",
                   "instock_code": "入库仓库",
                   "receive_address": "卸货地址",
                   "price_per_ton": "吨公里/价格",
                   "remark": "备注(配件)"
               },
               inplace=True)

    df1.rename(index=str,
               columns={
                   "city": "城市",
                   "end_point": "区县",
                   "big_commodity": "大品种",
                   "weight": "总重量",
                   "load_num": "区县总车次数"
               },
               inplace=True)
    df.to_excel(writer, sheet_name="分货车次明细")
    df1.to_excel(writer, sheet_name="分货车次汇总")
    writer.save()


if __name__ == '__main__':
    generate_excel()
