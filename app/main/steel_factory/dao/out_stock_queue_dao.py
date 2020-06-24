# -*- coding: utf-8 -*-
# Description: 排队信息
# Created: shaoluyu 2020/06/16
from app.util.base.base_dao import BaseDao


class OutStockQueueDao(BaseDao):
    def select_out_stock_queue(self):
        """
        查询仓库排队信息
        :return:
        """
        sql = """
        select
        stock_name
        from
        (
        SELECT
        CONCAT(stock_code,'-',stock_name) as stock_name,
        (dis_bill_no_jc_trucks_count+dis_cw_trucks_count+dis_jh_trucks_count+dis_jc_no_sign_trucks_count+dis_in_warehouse_trucks_count) as truck_count
        FROM
        db_dev.`dws_dis_warehouse_trucks`
        ) t
        where truck_count > 35
        """
        data = self.select_all(sql)
        out_stock_list = list()
        if data:
            for i in data:
                code, = i.values()
                out_stock_list.append(code)
        return out_stock_list


out_stock_queue_dao = OutStockQueueDao()
