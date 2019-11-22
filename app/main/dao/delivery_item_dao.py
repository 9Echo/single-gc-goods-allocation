# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 17:13
# @Author  : Zihao.Liu

from app.main.dao.base_dao import BaseDao
from app.main.entity.delivery_item import DeliveryItem
from app.utils.date_util import get_now_str


class DeliveryItemDao(BaseDao):

    def get_by_sheet(self, sheet_id):
        """根据发货单号获取所有的子发货单"""
        sql = "select * from t_ga_delivery_item where delivery_no = %s"
        values = (sheet_id,)
        results = self.select_all(sql, values)
        return [DeliveryItem(row) for row in results]

    def batch_insert(self, items):
        """批量插入子发货单"""
        sql = """insert into t_ga_delivery_item(
            delivery_no,
            delivery_item_no,
            order_no,
            dest,
            product_type,
            spec,
            weight,
            warehouse,
            quantity,
            free_pcs,
            total_pcs,
            create_time) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        if items:
            values = [(
                item.delivery_no,
                item.delivery_item_no,
                item.order_no,
                item.dest,
                item.product_type,
                item.spec,
                item.weight,
                item.warehouse,
                item.quantity,
                item.free_pcs,
                item.total_pcs,
                get_now_str()) for item in items]
            self.executemany(sql, values)
        return

    def batch_update(self, items):
        """批量更新子发货单"""
        sql = """update t_ga_delivery_item set 
                quantity= %s,
                free_pcs= %s
                where delivery_item_no = %s"""
        if items:
            values = [(
                delivery_item.quantity,
                delivery_item.free_pcs,
                delivery_item.delivery_item_no) for delivery_item in items]
            self.executemany(sql, values)

    def batch_delete(self, delivery_item):
        """批量删除子发货单"""
        sql = "delete from t_ga_delivery_item where delivery_item_no = %s"
        if delivery_item:
            values = [(item.delivery_item_no,) for item in delivery_item]
            self.executemany(sql, values)


delivery_item_dao = DeliveryItemDao()


if __name__ == '__main__':
    # with open('E:\JC\delivery.txt', 'r',encoding='UTF-8') as f:
    #     datas = json.loads(f.read())
    # # 创建发货通知单实例，初始化属性
    # delivery = DeliverySheet(datas["data"])
    # print(delivery),
    delivery_item_dao.update([('1', 'abcde1'), ('2', 'abcde2')])

