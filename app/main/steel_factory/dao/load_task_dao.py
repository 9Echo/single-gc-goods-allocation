from app.util.base.base_dao import BaseDao
import datetime


class LoadTaskDao(BaseDao):
    """
    LoadTask相关数据库操作
    """
    def insert_load_task(self, values):
        """增
        Args:

        Returns:

        Raise:

        """
        sql = """
            insert into db_model_dev.t_load_task(
            company_id,
            load_task_id,
            load_task_type,
            total_weight,
            city,
            end_point,
            price_per_ton,
            total_price,
            remark,
            priority_grade,
            create_id,
            `create_date`
            ) 
            value(%s, %s, %s, %s, %s,
                   %s, %s, %s, %s, %s, 
                   %s, %s)
        """
        self.executemany(sql, values)

    def delete_load_task(self):
        """删

        Args:

        Returns:

        Raise:

        """
        sql = """
            delete from {} 
            where
        """

    def update_load_task(self):
        """改

        Args:

        Returns:

        Raise:

        """
        sql = """
            update {} set {}={},
            where
        """

    def select_load_task(self):
        """查

        Args:

        Returns:

        Raise:

        """
        sql = """
            select * 
            from {}
            where 
        """


load_task_dao = LoadTaskDao()
if __name__ == "__main__":
    # ('C000000882', -1, '甩货', 22802.212, None, None, 0, 0, '垫皮,鞍座,草垫子,垫木,钢丝绳', 'A', 'ct', datetime.datetime(2020, 5, 28, 15, 35, 51, 453957)
    load_task_dao.insert_load_task(
        [('C000000882', -1, '甩货', 22802.212, None, None, 0, 0, '垫皮,鞍座,草垫子,垫木,钢丝绳', 'A', 'ct', datetime.datetime(2020, 5, 28, 15, 35, 51, 453957))])