from app.main.dao.base_dao import BaseDao


class ComposeDao(BaseDao):

    """

    """

    def get_compose_items(self, customer_id_list, product_type_list):
        sql = """
        select
        i.*
        from
        (SELECT delivery_no, customer_id from `t_ga_delivery_sheet` where `status` = 'FHZT00') s
        left join t_ga_delivery_item i on s.delivery_no = i.delivery_no and s.customer_id in ({})
        where product_name in ({})
        
        """
        #
        cus_values = "'"
        cus_values += "','".join([i for i in customer_id_list])
        cus_values += "'"
        #
        pro_values = "'"
        pro_values += "','".join([i for i in product_type_list])
        pro_values += "'"
        data = self.select_all(sql.format(cus_values, pro_values))
        return data


















compose_dao = ComposeDao()