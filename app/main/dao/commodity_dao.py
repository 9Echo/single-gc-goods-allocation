from app.main.db_pool import db_pool_ods, db_pool_trans_plan
import traceback


def get_commodity():
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
        from db_dw.ods_db_inter_t_keeperhd k1 join db_dw.ods_db_inter_t_keeperln k2 on k1.id = k2.main_id) t1,
        db_dw.ods_db_inter_t_orderhd t2
        where t1.docuno = t2.HXDH ) t4
        where t3.main_product_list_no = t4.docuno 
        ORDER BY t3.travel_no, t3.create_date
        """
        conn = db_pool_ods.connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print("commodity_dao.get_commodity is error")
        traceback.print_exc()
    finally:
        conn.close()


def write_database(data):
    """写库

    Args:
        data:要写入的数据  形如：[主品名，搭配品名，搭配次数]

    Returns:

    Raise:

    """
    try:
        sql = """
            insert into db_trans_plan.t_compose_commodity(main_commodity,match_commodity,match_size) 
            values('{}', '{}', '{}')
        """
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        cursor.execute(sql.format(data[0], data[1], data[2]))
        conn.commit()
    except Exception as e:
        print("commodity_dao.write_database is error")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


def truncate_table(tablename):
    """清除数据

    Args:
        tableName：清除的数据库名

    Returns:

    Raise:

    """
    try:
        sql = """
            truncate table {}  
        """
        conn = db_pool_trans_plan.connection()
        cursor = conn.cursor()
        cursor.execute(sql.format(tablename))
        conn.commit()
    except Exception as e:
        print("commodity_dao.delete_data is error")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    results = get_commodity()
    print(results)