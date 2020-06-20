from app.util.base.base_dao import BaseDao


class OutStockQueueDao(BaseDao):
    def select_out_stock_queue(self):
        """
        查询仓库排队信息
        :return:
        """
        sql = """
        SELECT
        stock_code
        FROM
        (
        SELECT
        q.*,
        d.trans_company_id,
        d.plan_no,
        p.plan_status,
        CASE
        WHEN q.STATUS = 'product_disp_queue_status_00' 
        OR q.STATUS = 'product_disp_queue_status_21' 
        OR q.STATUS = 'product_disp_queue_status_22' THEN
        '1' 
        WHEN q.STATUS = 'product_disp_queue_status_30' 
        OR q.STATUS = 'product_disp_queue_status_37' THEN
        '2' 
        WHEN q.STATUS = 'product_disp_queue_status_38' THEN
        '3' 
        WHEN q.STATUS = 'product_disp_queue_status_40' THEN
        '4' 
        WHEN q.STATUS = 'product_disp_queue_status_50' THEN
        '5' ELSE q.STATUS 
        END AS status_type,
        CASE
            
            WHEN q.whether_remind = 1 THEN
            '是' ELSE '否' 
        END AS whether_remind_name 
        FROM
        ods_db_queue_t_product_disp_entry_queue q
        LEFT JOIN ods_db_queue_t_product_disp_procure_deal d ON q.deal_id = d.deal_id
        LEFT JOIN ods_db_queue_t_plan p ON d.plan_no = p.plan_no 
        WHERE
        1 = 1 
        AND q.queue_type = 3 
        AND q.company_id = 'C000002000' 
        AND p.plan_status = 'DDZT68' 
        AND q.STATUS REGEXP '^(product_disp_queue_status_3|product_disp_queue_status_4|product_disp_queue_status_5)' 
        ) t 
        WHERE
        1 = 1 
        AND DATE_SUB( CURDATE( ), INTERVAL 1 DAY ) <= date( QUEUE_START_TIME ) 
        GROUP BY
        stock_code 
        HAVING count(1)>35
        """
        data = self.select_all(sql)
        out_stock_list = list()
        if data:
            for i in data:
                code, = i.values()
                out_stock_list.append(code)
        return out_stock_list


out_stock_queue_dao = OutStockQueueDao()
