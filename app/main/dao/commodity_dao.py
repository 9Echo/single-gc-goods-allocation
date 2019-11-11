from app.main.db_pool import db_pool_ods, db_pool_trans_plan
import traceback
import pandas as pd
from datetime import datetime
import time


def get_commodity(start_date="2019-10-12"):
    """读数据
    关于车牌、品种、发货单、发货单创建时间、运单创建时间、结算单创建时建的数据

    Args:

    Returns:
        results:读到的数据

    Raise:

    """
    try:
        sql = """
            select t4.docuno,keeper_time,t3.travel_no,t4.productname, 
        t3.create_date waybill_time,t4.crted_date order_time
        -- t3.waybill_no,
        from db_dw.ods_db_trans_t_waybill t3,
        (select t1.docuno,t2.crted_date,t1.productname,t1.crted_date keeper_time
        from (select k1.docuno,k2.productname,k1.crted_date
        from db_dw.ods_db_inter_t_keeperhd k1 join db_dw.ods_db_inter_t_keeperln k2 on k1.id = k2.main_id
        where timestampdiff(second, k1.crted_date, '{}')<0 and timestampdiff(second, k1.crted_date, '{}')>0) t1,
        db_dw.ods_db_inter_t_orderhd t2
        where t1.docuno = t2.HXDH ) t4
        where t3.main_product_list_no = t4.docuno 
        ORDER BY t3.travel_no, t3.create_date
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        list = str(start_date).split(" ")
        conn = db_pool_ods.connection()
        cursor = conn.cursor()
        cursor.execute(sql.format(list[0], now))
        results = cursor.fetchall()
        return results, now
    except Exception as e:
        print("commodity_dao.get_commodity is error")
        traceback.print_exc()
    finally:
        conn.close()


def write_database(data):
    """写库

    Args:
        data:要写入的数据  形如：[主品名，搭配品名，搭配次数，更新时间]

    Returns:

    Raise:

    """
    try:
        sql = """
            insert into db_trans_plan.t_compose_commodity(main_commodity,match_commodity,match_size,update_time) 
            values('{}', '{}', '{}', '{}')
        """
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        cursor.execute(sql.format(data[0], data[1], data[2], data[3]))
        conn.commit()
        update_database_time(data[3])
    except Exception as e:
        print("commodity_dao.write_database is error")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


def update_database_size(data):
    """更新数据库

    Args:
        data:要写入的数据  形如：[主品名，搭配品名，搭配次数, 更新时间]

    Returns:

    Raise:

    """
    try:
        sql = """
            update db_trans_plan.t_compose_commodity 
            set match_size = '{}'
            where main_commodity = '{}' and match_commodity = '{}'
        """
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        cursor.execute(sql.format(data[2], data[0], data[1]))
        conn.commit()
    except Exception as e:
        print("commodity_dao.update_database_size is error")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


def update_database_time(data):
    """更新数据库时间

    Args:
        data:要写入的数据  形如：update_time

    Returns:

    Raise:

    """
    try:
        sql = """
            update db_trans_plan.t_compose_commodity 
            set  update_time = '{}'
        """
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        cursor.execute(sql.format(data))
        conn.commit()
    except Exception as e:
        print("commodity_dao.update_database_time is error")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


def pd_read_table(tablename):
    """读数据

    Args:
        tableName：读的数据库名

    Returns:

    Raise:

    """
    try:
        sql = """
            select *
            from {}
        """
        conn = db_pool_trans_plan.connection()
        results = pd.read_sql_query(sql.format(tablename), conn)
        return results
    except Exception as e:
        print("commodity_dao.read_table is error")
        traceback.print_exc()


if __name__ == '__main__':
    results = get_commodity()
