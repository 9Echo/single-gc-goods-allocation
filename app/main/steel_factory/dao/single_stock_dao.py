from app.util.base.base_dao import BaseDao


class StockDao(BaseDao):
    def select_stock(self):
        """
        查询库存
        :return:
        """

        sql = """
        SELECT
        NOTICENUM as notice_num,
        PURCHUNIT as consumer,
        ORITEMNUM as oritem_num, 
        DEVPERIOD as devperiod, 
        DELIWAREHOUSE as deliware_house, 
        COMMODITYNAME as commodity_name,
        t2.prod_kind_price_out as big_commodity_name,
        PACK as pack,  
        MATERIAL as mark, 
        STANDARD as specs, 
        DELIWARE as deliware, 
        PORTNUM, 
        DETAILADDRESS as detail_address, 
        PROVINCE as province, 
        CITY as city, 
        WAINTFORDELNUMBER as waint_fordel_number, 
        WAINTFORDELWEIGHT as waint_fordel_weight, 
        CANSENDNUMBER, 
        CANSENDWEIGHT, 
        DLV_SPOT_NAME_END as dlv_spot_name_end, 
        PACK_NUMBER, 
        NEED_LADING_NUM, 
        NEED_LADING_WT, 
        OVER_FLOW_WT, 
        LATEST_ORDER_TIME as latest_order_time, 
        PORT_NAME_END as port_name_end
    FROM
        ods_db_inter_bclp_can_be_send_amount t1,
        (
        SELECT
            prod_kind,
            CASE WHEN 
            locate('型钢',prod_kind_price_out)>0
            THEN
            '型钢'
            when 
            locate('螺纹',prod_kind_price_out)>0
            then '螺纹'
        ELSE
            prod_kind_price_out
    END as prod_kind_price_out
    
        FROM
            db_dw.ods_db_sys_t_prod_spections ps 
        WHERE
            ps.company_id = 'C000000882' 
            AND is_use = 'SYBJ10'
            and prod_kind_price_out is not null
        GROUP BY
            prod_kind 
        ) t2 
    WHERE
        t1.`STATUS`!='D'
        AND t1.COMMODITYNAME = t2.prod_kind
        AND DELIWARE IN ( ' -', 'U123-连云港东泰码头(外库)','U124-连云港东联码头(外库)','U210-董家口库','U220-赣榆库','U288-岚北港口库2' ) 
        AND PURCHUNIT NOT IN ( '日照钢铁供应有限公司', '日照京华管业有限公司' ) 
            """
        data = self.select_all(sql)
        return data


stock_dao = StockDao()
