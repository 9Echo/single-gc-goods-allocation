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
            BIG_COMMODITYNAME as big_commodity_name,
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
            PORT_NAME_END as port_name_end,
            priority
        from
        db_ads.kc_rg_product_can_be_send_amount
        """
        # concat(longitude, latitude) as standard_address
        data = self.select_all(sql)
        return data


stock_dao = StockDao()
