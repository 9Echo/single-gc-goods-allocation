from app.main.dao.company_dao import get_company_data, write_database
import time
import traceback


class Company:

    def analysis(self):
        try:
            data = get_company_data()
            # {waybill_no, create_date, travel_no, f_docuno, b_docuno, order_cal,
            # SJGBSL, org_unit_name, f_crted_date, j_crted_date}
            # {运单号，运单create_date，车牌号， 发货通知单号，结算单号， 理重，
            # 实重， 公司名， 发货create_date, 结算create_date }
            # print(data)

            # {车牌号:[运单号，运单create_date，发货通知单号，结算单号，公司名，结算create_date],... }
            analysis_dic = {}
            for index, row in data.iterrows():
                if row['travel_no'] not in analysis_dic:
                    analysis_dic[row['travel_no']] = []
                analysis_dic[row['travel_no']].append([row['waybill_no'], row['create_date'], row['f_docuno'],
                                                       row['b_docuno'], row['org_unit_name'], row['j_crted_date']])
            # print(analysis_dic)

            # 判定为同一车的条件：发货通知单号、结算单号、公司名不同，
            # 两条数据的运单时间、结算单时间分别相差小于1小时
            company_list = []
            for k in analysis_dic:
                if len(analysis_dic[k]) != 1:
                    # print(k, analysis_dic[k])
                    # 为了避免重复，新建了一个列表，将每辆车已录入company_list的组合记录下来
                    comp = []
                    for i in analysis_dic[k]:
                        for j in analysis_dic[k]:
                            i5 = int(time.mktime(i[5].timetuple()))
                            j5 = int(time.mktime(j[5].timetuple()))
                            if i[2] != j[2] and i[3] != j[3] and i[4] != j[4] \
                                    and abs(i5 - j5) < 3600:
                                comp1 = [i[0], j[0]]
                                comp2 = [j[0], i[0]]
                                if comp1 not in comp and comp2 not in comp:
                                    comp.append([i[0], j[0]])
                                    company_list.append([i[4], j[4]])
                                    # print(k, i, 'i')
                                    # print(k, j, 'j')
            # print(company_list)

            # 添加拼车次数列
            # {('公司1', '公司2'): 拼车次数,...}
            result_dic = {}
            for li in company_list:
                company_con1 = (li[0], li[1])
                company_con2 = (li[1], li[0])
                if company_con1 not in result_dic and company_con2 not in result_dic:
                    result_dic[company_con1] = 1
                else:
                    if company_con1 in result_dic:
                        result_dic[company_con1] = result_dic[company_con1] + 1
                    elif company_con2 in result_dic:
                        result_dic[company_con2] = result_dic[company_con2] + 1
            # print(result_dic)

            # 按拼车次数给结果排序，由大到小
            result = sorted(result_dic.items(), key=lambda x: x[1], reverse=True)
            print(result)
            # 输出结果
            for re in result:
                print(re)
            # 写库
            write_database(result)
        except Exception as e:
            print("compose_company analysis error!")
            traceback.print_exc()


if __name__ == '__main__':
    com = Company()
    com.analysis()
