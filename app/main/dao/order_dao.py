# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:10
# @Author  : Zihao.Liu
# Modified: shaoluyu 2019/11/13

from app.main.dao.base_dao import BaseDao
from app.main.entity.order import Order
from app.main.entity.order_item import OrderItem
from app.utils.date_util import get_now_str


class OrderDao(BaseDao):

    def get_one(self, order_no):
        # 查询订单
        sql = "select * from t_ga_order where order_no=%s"
        values = (order_no,)
        order = Order(self.select_one(sql, values))
        # 查询订单项
        sql = "select * from t_ga_order_item where order_no=%s"
        results = self.select_all(sql, values)
        order.items = [OrderItem(row) for row in results]
        return order

    def get_all(self):
        """获取所有订单"""
        sql = """select o.*, oi.*, oi.rid as irid, oi.create_time as ict, oi.update_time as iut 
            from t_ga_order o 
            left join t_ga_order_item oi on o.order_no=oi.order_no
            order by o.rid"""
        results = self.select_all(sql)
        order_dict = {}
        # 将订单项结果合并到订单中
        for row in results:
            if not order_dict.__contains__(row['order_no']):
                order_dict[row['order_no']] = Order(row)
            if row['irid'] is not None:
                row['rid'] = row['irid']
                row['create_time'] = row['ict']
                row['update_time'] = row['iut']
                order_dict[row['order_no']].items.append(OrderItem(row))
        return [order for order in order_dict.values()]

    def insert(self, order):
        # 保存订单
        sql = """insert into t_ga_order(
            order_no,
            customer_id,
            salesman_id,
            create_time) value (%s,%s,%s,%s)"""
        values = (
            order.order_no,
            order.customer_id,
            order.salesman_id,
            get_now_str())
        self.execute(sql, values)
        # 保存订单项
        if order.items:
            sql = """ insert into t_ga_order_item(
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
                get_now_str()) for item in order.items]
            self.executemany(sql, values)


order_dao = OrderDao()
