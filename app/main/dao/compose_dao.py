from app.main.dao.base_dao import BaseDao


class ComposeDao(BaseDao):

    """
    筛选可推荐的预留提货单
    """

    def get_compose_delivery(self, company_id, customer_id_list, delivery_no_list):
        sql = """
        SELECT 
        delivery_no, 
        customer_id,
        weight
        from 
        `t_ga_delivery_sheet` 
        where 
        `status` = 'FHZT00' and company_id = '{}' and customer_id in ({}) and delivery_no not in ({})


        
        """
        #客户条件
        if len(customer_id_list) == 1:
            cus_values = "'" + str(customer_id_list[0]) + "'"
        else:
            cus_values = "'"
            cus_values += "','".join([i for i in customer_id_list])
            cus_values += "'"

        # 提货单号条件
        if len(delivery_no_list) == 1:
            de_values = "'" + str(delivery_no_list[0]) + "'"
        else:
            de_values = "'"
            de_values += "','".join([i for i in delivery_no_list])
            de_values += "'"
        data = self.select_all(sql.format(company_id, cus_values, de_values))
        return data


















compose_dao = ComposeDao()