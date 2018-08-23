# -*- coding: utf-8 -*-

import time
import rrdgraph
import MySQLdb
import mysql_graph
# Create your views here.

null = float(-1)
db_graph = mysql_graph.db_operate()

def re_ss(start_ss, *incounter):
    end = start_ss + 60

    conn_beacon = MySQLdb.connect('localhost', 'root', '123321', 'my_web')
    cur_beacon = conn_beacon.cursor()
    sql_host_graph = "select distinct endpoint from endpoint;"
    hostname = db_graph.mysql_command(sql_host_graph)

    endpoints= [endpoint[0] for endpoint in hostname]

    re = rrdgraph.graph_query(endpoints,[incounter[0]], start=start_ss, end=end)
    try:
        res = list(eval(re))
        z = []
        for i in res:
            a = i.values()[2]
            c = i.values()[4]
            sql_pc = "select 'hostname',a.abbr_name,a.abbr_name,a.abbr_name \
            from openfalcon_roomname as a" 

            cur_beacon.execute(sql_pc)
            proclu_temp = cur_beacon.fetchone()
            print(i,proclu_temp)
            if proclu_temp is None:
                pass
            else:
                if (i.values()[3] == []) or (i.values()[3] == -1.0):
                    b = float(0)
                else:
                    try:
                        b = i.values()[3][0].values()[1]
                    except Exception as e:
                        print (e)
                pr = proclu_temp[1]
                clu = proclu_temp[2]
                idc_name = proclu_temp[3]
                s = (a, b, c, pr, clu, idc_name, start_ss)
                z.append(s)
        conn_beacon.close()
    except Exception as e:
        pass
    return tuple(z)


def query_save(*incounter):
    start_ss = int(time.time()) - 60
    expire = start_ss - 300

    conn2 = MySQLdb.connect('127.0.0.1', 'root', '123321', 'my_web')
    cur2 = conn2.cursor()

    if incounter:
        if incounter[0] == 'ss.estab':
            sql_ss = "insert into  top10_date_graph(endpoint,value,counter,project,cluster,idc,add_date)values(%s,%s,%s,%s,%s,%s,%s);"
            sqlss_4 = "delete  from top10_date_graph where add_date < %s" % expire

            tmp_1 = re_ss(start_ss, *incounter)
            cur2.executemany(sql_ss, tmp_1)
            cur2.execute(sqlss_4)
            conn2.commit()
        else:
            pass
    conn2.close()


'''此脚本负责定时从query接口api查询数据和存储到mysql中(方便提取排序和处理)，以下罗列定时任务'''

query_save('ss.estab')
