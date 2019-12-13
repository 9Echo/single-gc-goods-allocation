from app.main.dao.base_dao import BaseDao


class ComposeDao(BaseDao):

    """
    筛选可推荐的预留提货单
    """

    def get_compose_delivery(self, company_id, customer_id_list):
        sql = """
        SELECT 
        delivery_no, 
        customer_id,
        weight
        from 
        `t_ga_delivery_sheet` 
        where 
        `status` = 'FHZT00' and company_id = '{}' and customer_id in ({})


        
        """
        #客户条件
        cus_values = "'"
        cus_values += "','".join([i for i in customer_id_list])
        cus_values += "'"
        data = self.select_all(sql.format(company_id, cus_values))
        return data


















compose_dao = ComposeDao()