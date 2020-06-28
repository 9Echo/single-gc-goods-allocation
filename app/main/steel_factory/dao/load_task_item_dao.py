# -*- coding: utf-8 -*-
# Description: 车次明细表
# Created: shaoluyu 2020/06/16
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
        # 1公司id 2车次号 3优先级 4重量 5件数 6城市 7终点 8大品名 9小品名 10发货通知单号
        # 11订单号 12收货用户 13规格 14材质 15出库仓库 16入库仓库 17收货地址 18最新挂单时间 19创建人id 20创建时间
        sql = """
            insert into t_load_task_item(
            company_id,
            schedule_no,
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
                   %s, %s, %s, %s, %s,
                   %s)
        """

        self.executemany(sql, values)

    def select_load_task_items(self):
        self.select_all()
        sql = """
            select * 
            from {}
            where 
        """


load_task_item_dao = LoadTaskItemDao()

# if __name__ == "__main__":
#     load_task_item_dao.insert_load_task_item([('C000000882', '202005281659941', '', 29.33, 1, '泰安市', '岱岳区', '西区黑卷',
#                                                '热轧卷板', 'F2004140594', 'DH2004140174001', '杭州热联集团股份有限公司', '2*1,500',
#                                                'Q235B', 'P8-P8精整黑卷成品库', ' -', '山东省泰安市岱岳区满庄钢材市场泰安中远库',
#                                                '2020-05-07 23:11:09.0', 'ct',
#                                                datetime.datetime(2020, 5, 28, 17, 4, 56, 399094))])
