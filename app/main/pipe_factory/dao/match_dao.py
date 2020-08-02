# -*- coding: utf-8 -*-
# Description: 
# Created: shaoluyu 2020/8/2 15:45
from app.util.base.base_dao import BaseDao


class MatchDao(BaseDao):
    def select_match_data(self, order, max_delivery_items, min_delivery_items):
        sql = """
        select
        a.*
        from
        t_gc_history_match a,(SELECT city_name FROM `t_company_address` where company_id = '{}') b
        where
        a.city_name = b.city_name 
        and
        a.main_item_id in ({}) and (a.sub_item_id in ({}) or ifnull(a.sub_item_id,'') = '')
        order by a.main_item_id,a.combine_count desc
        """
        max_item_id_values = "'"
        max_item_id_values += "','".join([i.item_id for i in max_delivery_items])
        max_item_id_values += "'"
        min_item_id_values = "'"
        min_item_id_values += "','".join([i.item_id for i in min_delivery_items])
        min_item_id_values += "'"
        return self.select_all(sql.format(order.customer_id, max_item_id_values, min_item_id_values))


match_dao = MatchDao()
