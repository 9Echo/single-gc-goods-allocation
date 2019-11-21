# -*- coding: utf-8 -*-
# @Time    : 2019/11/14 16:11
# @Author  : Zihao.Liu
from app.main.dao.base_dao import BaseDao
from app.main.entity.order_item_left import OrderItemLeft
from app.utils.date_util import get_now_str


class OrderItemLeftDao(BaseDao):

    def get_all(self):
        """查询所有尾单"""
        sql = "select * from t_ga_order_left_item"
        results = self.select_all(sql)
        return [OrderItemLeft(row) for row in results]

    def batch_insert(self, items):
        """批量插入尾单"""
        sql = """insert into t_ga_order_left_item(
            order_no, 
            product_type, 
            spec, 
            quantity, 
            free_pcs, 
            create_time) value(%s,%s,%s,%s,%s,%s)"""
        values = [(
            item.order_no,
            item.product_type,
            item.spec,
            item.quantity,
            item.free_pcs,
            get_now_str()) for item in items]
        self.executemany(sql, values)


order_item_left_dao = OrderItemLeftDao()
