from app.main.dao.connect_produce import conn, sql
import time

cursor = conn.cursor()
cursor.execute(sql)
results = cursor.fetchall()
data = {}
data2 = {}
for res in results:
    if res[2] not in data.keys():
        data[res[2]] = []
    data[res[2]].append([res[0],
                         res[3],
                         int(time.mktime(res[1].timetuple())),
                         int(time.mktime(res[4].timetuple())),
                         int(time.mktime(res[5].timetuple()))])
for i in data.keys():
    for j in data[i]:
        for q in range(len(data[i])):
            if abs(j[4] - data[i][q][4]) < 3600 and j[0] != data[i][q][0] and j[1] != data[i][q][1]:
                name = j[1] + ',' + data[i][q][1]
                data2[name] = data2.get(name, 0) + 1
print(data2)