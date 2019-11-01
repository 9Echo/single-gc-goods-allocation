import pymysql

conn = pymysql.connect("rm-bp105ft9dy0qc53y8wo.mysql.rds.aliyuncs.com",
                       "v3read",
                       "SamE57@7583jgpck",
                       charset="utf8")

sql = """
    select t4.docuno,keeper_time,t3.travel_no,t4.productname, t3.create_date waybill_time,t4.crted_date order_time
-- t3.waybill_no,
from db_trans.t_waybill t3,
(
select t1.docuno,t2.crted_date,t1.productname,t1.crted_date keeper_time
from (select k1.docuno,k2.productname,k1.crted_date
from db_inter.t_keeperhd k1 join db_inter.t_keeperln k2 on k1.id = k2.main_id) t1,db_inter.t_orderhd t2
where t1.docuno = t2.HXDH ) t4
where t3.main_product_list_no = t4.docuno 
ORDER BY t3.travel_no, t3.create_date
"""