import pandas as pd
from typing import List, Dict, Any, Tuple
from app.main.entity.load_task import LoadTask
from app.main.services.steel_dispatch_service import dispatch


def generate_excel(load_task_list: List[LoadTask]):
    df = pd.DataFrame([item.as_dict() for item in load_task_list])
    writer = pd.ExcelWriter("库存.xlsx")
    df.to_excel(writer, sheet_name="分货车次明细")

    df1 = df.groupby(['city', 'end_point', 'big_commodity']).agg(
        {'weight': 'sum'}).reset_index()
    df2 = df.groupby(['city', 'end_point'])['load_task_id'].nunique().reset_index()
    load_list = []
    for index, row in df1.iterrows():
        temp_df = df2[(df2['city'] == row['city']) & (df2['end_point'] == row['end_point'])]

        load_list.append(list(temp_df['load_task_id'])[0])
    # 增加新的一列车次数
    df1['load_num'] = load_list

    df1.rename(index=str,
               columns={
                   "city": "城市",
                   "end_point": "区县",
                   "big_commodity": "大品种",
                   "weight": "总重量",
                   "load_num": "车次数"
               },
               inplace=True)

    df1.to_excel(writer, sheet_name="分货车次汇总")
    writer.save()
    print(df1)


if __name__ == '__main__':
    generate_excel()
