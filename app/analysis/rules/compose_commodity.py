from app.main.dao.commodity_dao import get_commodity, write_database, truncate_table
import time
import traceback


def get_commodity_collcation():
    """品种搭配规则

    Args:

    Returns:
        data2: 品种搭配的字典  形如：{'焊管 1,热镀': 62,...}

    Raise:

    """
    try:
        # 得到从发货单、运单、结算单个别信息   形如：（发货通知单号，发货通知单创建时间，车牌，品种，发运单创建时间，结算单创建时间）
        results = get_commodity()
        # 将results整理成字典   形如：{车牌：[[发货单，品种，发货单创建时间，运单创建时间，结算单创建时间],...],...}其中时间为时间戳
        data = {}
        # 拼命搭配字典    形如： {'主品名,搭配品名':次数,...}
        data2 = {}
        # 循环 results
        for res in results:
            # 如果车牌不在data的键中，则创建
            if res[2] not in data.keys():
                data[res[2]] = []
            # 给该车牌 添加数据
            data[res[2]].append([res[0],
                                 res[3],
                                 int(time.mktime(res[1].timetuple())),
                                 int(time.mktime(res[4].timetuple())),
                                 int(time.mktime(res[5].timetuple()))])
        # 循环 data
        for i in data.keys():
            count = 0
            # 比较同一个车牌下的结算单创建时间
            for j in data[i]:
                count += 1
                for q in range(len(data[i])-count):
                    p = q + count
                    # 将结算单创建时间 相近的且发货单不同的 视为拼货单
                    if abs(j[4] - data[i][p][4]) < 1800 and j[0] != data[i][p][0] and j[1] != data[i][p][1]:
                        # 合并品种搭配数据
                        if j[1] > data[i][p][1]:
                            temp = j[1]
                            j[1] = data[i][p][1]
                            data[i][p][1] = temp
                        # 将拼货的品种 用逗号连接 并记录次数
                        name = j[1] + ',' + data[i][p][1]
                        data2[name] = data2.get(name, 0) + 1
        data2 = sorted(data2.items(), key=lambda x: x[0])
        # 清除 t_compose_commodity 数据
        truncate_table("t_compose_commodity")
        # 写库
        for i in data2:
            list1 = i[0].split(',')
            data3 = ([list1[0], list1[1], i[1]])
            write_database(data3)
        return data2
    except Exception as e:
        print("compose_commodity.py is error")
        traceback.print_exc()


if __name__ == "__main__":
    get_commodity_collcation()