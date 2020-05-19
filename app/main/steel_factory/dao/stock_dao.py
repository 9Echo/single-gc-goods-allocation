from app.util.base.base_dao import BaseDao
from datetime import datetime
import datetime as dt


class StockDao(BaseDao):
    def select_stock(self):
        """获取0点库存

        Args:

        Returns:

        Raise:

        """
        date = datetime.now().date() + dt.timedelta(-1)
        sql = """
                SELECT
                    t2.prod_kind_price_out as prod_kind_price_out,
                    * 
                FROM
                    db_dev.dwd_db_inter_bclp_can_be_send_amount_day t1,
                    (
                        SELECT
                            prod_kind,
                            prod_kind_price_out 
                        FROM
                            db_dw.ods_db_sys_t_prod_spections ps 
                        WHERE
                            ps.company_id = 'C000000882' 
                            AND ps.length_start = 0 
                            AND ps.length_end = 0 
                            AND is_use = 'SYBJ10' 
                        GROUP BY
                            prod_kind 
                    ) t2 
                WHERE
                    record_day = '{}' 
                    AND PRODCOMPANY NOT IN ( '日照钢铁供应有限公司', '日照京华管业有限公司' ) 
                    AND t1.COMMODITYNAME = t2.prod_kind
                    AND t1.CANSENDNUMBER > 0
                    AND t1.CANSENDWEIGHT is not NULL
                    AND t1.CITY not in ('青岛市','临沂市','日照市')
            """
        data = self.select_all(sql.format(date))
        return data
