import pandas as pd
from typing import List, Dict, Any, Tuple
from app.main.entity.load_task import LoadTask
from app.main.services.steel_dispatch_service import dispatch

def generate_excel():
    # load_task_list=dispatch()
    load_task_list2=[]
    load_task_list=[]
    load_task1= LoadTask()
    load_task2= LoadTask()
    load_task1.city='泰安市'
    load_task1.commodity='冷成形纵切钢带'
    load_task1.count=4.0
    load_task1.end_point='新泰市'
    load_task1.instock_code='-'
    load_task1.load_task_id=1
    load_task1.notice_num='F2004090342'
    load_task1.oritem_num='DF2004090037002'
    load_task1.outstock_code='F20-运输处临港西库'
    load_task1.priority=None
    load_task1.sgsign='RECC'
    load_task1.standard='1.2*30'
    load_task1.total_weight=32435.636363634
    load_task1.type=None
    load_task1.weight=912.0
    load_task1=load_task1.as_dict()

    load_task2.city = '泰安市'
    load_task2.commodity = '冷成形纵切钢带'
    load_task2.count = 10.0
    load_task2.end_point = '新泰市'
    load_task2.instock_code = '-'
    load_task2.load_task_id = 1
    load_task2.notice_num = 'F2004090342'
    load_task2.oritem_num = 'DF2004090037001'
    load_task2.outstock_code = 'F20-运输处临港西库'
    load_task2.priority = None
    load_task2.sgsign = 'RECC'
    load_task2.standard = '1.2*407'
    load_task2.total_weight = 32435.636363634
    load_task2.type = None
    load_task2.weight =31523.63636363
    load_task2 = load_task2.as_dict()

    load_task_list.append(load_task1)
    load_task_list.append(load_task2)
    df=pd.DataFrame(load_task_list)
    df.to_excel("sheet3.xls")
    df.drop_duplicates(subset=['load_task_id'],keep='first',inplace=True)
    group_df1=df.groupby(['city', 'end_point']).agg({'total_weight':['sum'],'load_task_id':['count']}).reset_index()
    group_df1.rename(index=str,
                     columns={
                         "city": "城市",
                         "end_point": "区县",
                         "commodity": "品种",
                         "sum": "总重量",
                         "count": "车次数"
                     },
                     inplace=True)

    print(group_df1)


if __name__ == '__main__':
    generate_excel()





