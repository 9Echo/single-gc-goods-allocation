import pandas as pd
from app.main.db_pool import db_pool_trans_plan, db_pool_ods
import traceback


def get_company_data():
    try:
        conn = db_pool_ods.connection()
        sql = """
            SELECT
        tw.waybill_no,
        tw.create_date as create_date,
        tw.travel_no as travel_no,
        tf.*
        FROM (
        select
        f_docuno,
        b_docuno,
        order_cal,
        SJGBSL,
        org_unit_name,
        f_crted_date,
        j_crted_date
        from (
        select
        tab_f.docuno as f_docuno, -- 发货通知单号
        tab_j.docuno as b_docuno, -- 结算单号
        order_cal, -- 理重
        -- (case when SJGBSL then SJGBSL*1000 end) as
        SJGBSL,-- 实重
        tab_f.org_unit_name as org_unit_name,-- 客户名
        tab_f.crted_date as f_crted_date,
        tab_j.crted_date as j_crted_date
        from (

        SELECT
        docuno, -- 发货通知单号
        org_unit, -- 客户id
        org_unit_name, -- 客户名称
        crted_date, -- 创建时间
        f_whscode, -- 提货库区id
        f_whsname, -- 提货库区名称
        order_j, -- 总件数
        order_g, -- 散根
        order_zg00, -- 总根数
        fee_order, -- 运费
        order_cal, -- 理重合计
        bath_no, -- 批次号
        data_address -- 数据来源  0010：衡水  0020：唐山
        FROM db_dw.ods_db_inter_t_keeperhd
        -- where crted_date BETWEEN '2019-10-27 00:00:00' and '2019-10-27 23:59:59'
        ) as tab_f
        left join
        (
        SELECT
        doctype, -- 单子类型
        docuno, -- 结算单号
        HXDH,  -- 发货通知单号
        org_unit,  -- 客户id
        org_unit_name, -- 客户名称
        crted_date, -- 创建时间
        f_whsid, -- 提货库区ID
        f_whsname, -- 提货库区名称
        f_amt, -- 运费
        SJGBSL, -- 结算重量
        bath_no, -- 批次号
        data_address -- 业务来源（0010：衡水，0020：唐山，0030：成都，0040：吉林，0050：郑州，0060：日照，0070：广州）
        FROM db_dw.ods_db_inter_t_orderhd

        ) as tab_j
        on tab_f.docuno = tab_j.HXDH
        where tab_j.docuno is not NULL
        order by tab_f.docuno

        ) as tab
        ) as tf
        left join
        (SELECT
        waybill_no,
        main_product_list_no,
        create_date,
        travel_no
        FROM db_dw.ods_db_trans_t_waybill
        where company_id = 'C000000888')as tw
        on tw.main_product_list_no = tf.f_docuno
        where travel_no is not null

            """
        data = pd.read_sql(sql, conn)
        return data
    except Exception as e:
        print("get_company_data error")
        traceback.print_exc()
    finally:
        conn.close()


def write_database(result):
    """
    :return:
    """
    try:
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        sql = "insert into t_compose_company(company_name1, company_name2, compose_num) values('{}','{}','{}')"
        for re in result:
            # print(re[0][0])
            # print(re[1])
            cursor.execute(sql.format(re[0][0], re[0][1], re[1]))
        print("finish!")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("write_database error!")
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    get_company_data()