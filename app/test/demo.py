import requests
import pymysql
import re
import threading

# mysql连接

host = "am-bp16yam2m9jqm2tyk90650.ads.aliyuncs.com"

user_name = "bigdata_user3"

password = "user2!1012"

conn = pymysql.connect(host=host, user=user_name, port=3306, password=password)

cur = conn.cursor()


def phone_verify(phone):
    res = requests.get(f'https://tcc.taobao.com/cc/json/mobile_tel_segment.htm?tel={phone}')
    # bs = bs4.BeautifulSoup(res.text, 'html5lib')
    # print(res.text)
    phone_stutas = ''
    carrier = re.findall(r"carrier:'(.*)'", res.text)
    if len(carrier) != 0:
        phone_stutas = carrier[0]
    else:
        phone_stutas = '手机号不规范'

    # if bs.find('div' ,{'class': 'upper_text'}) is None :
    #     print(bs)
    #     print(bs.find('div', {'class': 'not_found_text'}).string)
    #     phone_stutas = bs.find('div', {'class': 'not_found_text'}).string
    # else:
    #     print(bs.find('div', {'class': 'upper_text'}).string)
    #     phone_stutas = bs.find('div', {'class': 'upper_text'}).string
    return phone_stutas


sql_str = 'SELECT user_id, mobile FROM	db_dev.dwd_db_sys_t_user WHERE phone_status = \'\' limit 5'
cur.execute(sql_str)

res = cur.fetchall()

sql_updates = ''
for r in res:
    user_id = r[0]
    phone = r[1]
    print(user_id, phone)
    phone_status_new = ''
    if len(phone) != 11:
        phone_status_new = '手机号不规范'
    else:
        phone_status_new = phone_verify(phone)
    try:
        sql_update = "update db_dev.dwd_db_sys_t_user set phone_status='{}' where user_id='{}';".format(
            phone_status_new, user_id)
        # print(sql_update)
        # cur.execute(sql_update)
    except:
        print('出错的SQL：' + sql_update)
        continue
    sql_updates += sql_update

sql_updates = sql_updates[:-1]
print(sql_updates)
count = cur.executemany(sql_updates, None)
conn.close()
