from app.util.base.base_dao import BaseDao


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
            create_date,
            ) 
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
