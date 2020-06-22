# -*- coding: utf-8 -*-
# Description: 已开装车清单数据
# Created: shaoluyu 2020/06/16
from app.util.base.base_dao import BaseDao


class LoadingDetailDao(BaseDao):
    def select_loading_detail(self):
        """
        查询人工已开单信息、预开单信息、模型推荐未确认信息
        :return:
        """

        sql = """
        SELECT 
            schedule_no,
            notice_num,
            oritem_num,
            outstock_name,
            weight,
            `count`
        FROM 
            db_ads.`kc_rg_valid_loading_detail`
        UNION ALL
        select
            schedule_no,
            notice_num,
            oritem_num,
            outstock_code,
            weight,
            `count`
        from 
            db_model.t_load_task_item
        where 
            create_date >= (SELECT
        IF
            ( MAX( CREATTIME ) > MAX( ALTERTIME ), MAX( CREATTIME ), MAX( ALTERTIME ) ) max_time
        FROM
            db_ads.kc_rg_product_can_be_send_amount)
        and 
             IFNULL(schedule_no,'') <> ''
        and 
          schedule_no not in (select DISTINCT schedule_no from db_ads.kc_rg_valid_loading_detail where schedule_no is not null)

        """
        data = self.select_all(sql)
        return data


loading_detail_dao = LoadingDetailDao()
