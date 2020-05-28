from app.util.base.base_dao import BaseDao


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
            create_date,
            )
            values('%s', '%s', '%s', '%s', '%s', 
                   '%s', '%s', '%s', '%s', '%s', 
                   '%s', '%s', '%s', '%s', '%s', 
                   '%s', '%s', '%s', '%s', '%s',)
        """
        self.executemany(sql, values)


load_task_item_dao = LoadTaskItemDao()