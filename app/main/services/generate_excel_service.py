import pandas as pd
from typing import List, Dict, Any, Tuple
from app.main.entity.load_task import LoadTask
from app.main.services.steel_dispatch_service import dispatch


def generate_excel(load_task_list: List[LoadTask]):
    df = pd.DataFrame([item.as_dict() for item in load_task_list])

    # df.to_excel("sheet3.xls")

    df1 = df.groupby(['city', 'end_point', 'commodity']).agg(
        {'weight': 'sum'}).reset_index()
    df2 = df.groupby(['city', 'end_point'])['load_task_id'].nunique().reset_index()
    load_list=[]
    for index, row in df1.iterrows():
        temp_df = df2[(df2['city'] == row['city']) & (df2['end_point'] == row['end_point'])]

        load_list.append(list(temp_df['load_task_id'])[0])
    # 增加新的一列车次数
    df1['load_num'] = load_list

    df1.to_excel("sheet3.xls")
    # df1.rename(index=str,
    #                  columns={
    #                      "city": "城市",
    #                      "end_point": "区县",
    #                      "sum": "总重量",
    #                      "count": "车次数"
    #                  },
    #                  inplace=True)
    print(df1)









if __name__ == '__main__':
    generate_excel()
