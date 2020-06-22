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
        `count`,
        'lms' as type
        FROM 
        `kc_rg_valid_loading_detail`
        UNION ALL
        select
        schedule_no,
        notice_num,
        oritem_num,
        outstock_code,
        weight,
        `count`,
        'model' as type
        from 
        db_model.t_load_task_item
        where 
        create_date >= (select max(max_time) from kc_rg_valid_loading_detail)
        and 
        schedule_no is not null
        """
        data = self.select_all(sql)
        return data


loading_detail_dao = LoadingDetailDao()
