from app.util.base.base_dao import BaseDao
import datetime


class LoadTaskItemDao(BaseDao):
    """
    LoadTaskItem相关数据库操作
    """

    def insert_load_task_item(self, values):
        """增

        Args:

        Returns:

        Raise:

        """
        sql = """
            insert into db_model_dev.t_load_task_item(
            company_id,
            load_task_id,
            priority,
            weight,
            `count`,
            city,
            end_point,
            big_commodity,
            commodity,
            notice_num,
            oritem_num,
            consumer,
            standard,
            sgsign,
            outstock_code,
            instock_code,
            receive_address,
            latest_order_time,
            create_id,
            `create_date`
            )
            value(%s, %s, %s, %s, %s, 
                   %s, %s, %s, %s, %s, 
                   %s, %s, %s, %s, %s, 
                   %s, %s, %s, %s, %s)
        """

        self.executemany(sql, values)


load_task_item_dao = LoadTaskItemDao()

if __name__ == "__main__":
    load_task_item_dao.insert_load_task_item([('C000000882', '202005281659941', '', 29.33, 1, '泰安市', '岱岳区', '西区黑卷', '热轧卷板', 'F2004140594', 'DH2004140174001', '杭州热联集团股份有限公司', '2*1,500', 'Q235B', 'P8-P8精整黑卷成品库', ' -', '山东省泰安市岱岳区满庄钢材市场泰安中远库', '2020-05-07 23:11:09.0', 'ct', datetime.datetime(2020, 5, 28, 17, 4, 56, 399094))])