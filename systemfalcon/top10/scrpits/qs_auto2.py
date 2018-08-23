# -*- coding: utf-8 -*-

import time
import MySQLdb
import rrdgraph
import config
import mysql_graph
# Create your views here.

null = float(-1)
db_graph = mysql_graph.db_operate()

def re_tu(start_ss, *incounter):
    end = start_ss + 60
    sql_host_graph = "select endpoint from endpoint;"
    hostname = db_graph.mysql_command(sql_host_graph)

    endpoints = [ endpoint[0] for endpoint in hostname]
    try:
        re = rrdgraph.graph_query(endpoints,[incounter[0]], start=start_ss, end=end)
        res = list(eval(re))
        z = []
        for i in res:
            a = i.values()[2]
            c = i.values()[4]
            cpu_num = 1
            if c == 'load.1min':
                if (i.values()[3] == []) or (i.values()[3] == -1.0) or (i.values()[3] is None):
                    b = float(-1)
                else:
                    b = i.values()[3][0].values()[1]
                if b is None:
                    b = float(-1)
                try:
                    load_percent = ('%.2f'%(b / cpu_num * 100))
                    s = (a, load_percent, c, start_ss, cpu_num)
                except Exception as e:
                    #print (" Load and CPU kernel arithmetic error is %s" % e)
                    pass
            elif c == 'cpu.idle':
                if (i.values()[3] == []) or (i.values()[3] == -1.0) or (i.values()[3] is None):
                    b = float(-1)
                elif i.values()[3][0].values()[1] is None:
                    b = float(-1)
                else:
                    b = ('%.2f' %(i.values()[3][0].values()[1]))
                cpu_u = 100 - float(b)
                cpu_use = 'cpu_use'
                s = (a, cpu_u, cpu_use, start_ss, cpu_num)
            else:
                if (i.values()[3] == []) or (i.values()[3] == -1.0) or (i.values()[3] is None):
                    b = float(-1)
                elif i.values()[3][0].values()[1] is None:
                    b = float(-1)
                else:
                    b = ('%.2f' %(i.values()[3][0].values()[1]))
                s = (a, b, c, start_ss, cpu_num)
            z.append(s)
    except:
        pass
    return tuple(z)


def re_nic(start_ss,*incounter):
    end = start_ss + 60

    conn1 = MySQLdb.connect('{0}'.format(config.DASHBOARD_DB_HOST), 'root', '123321', 'graph')
    cur1 = conn1.cursor()
    sql_host = "select distinct endpoint from endpoint"
    cur1.execute(sql_host)
    hostname = cur1.fetchall()

    endpoints = []
    nic_name='ens33'
    NET_OUT = ["net.if.out.bits/iface={0}".format(nic_name)]
    endpoints = [endpoint[0] for endpoint in hostname]
    re = rrdgraph.graph_query(endpoints,NET_OUT, start=start_ss, end=end)
    res = list(eval(re))
    z = []
    print(res)
    for i in res:
        a = i.values()[2]
        if (i.values()[3] == []) or (i.values()[3] == -1.0) or (i.values()[3] is None):
            b = float(-1)
        elif i.values()[3][0].values()[1] is None:
            b = float(-1)
        else:
            b = ("%.2f" % (i.values()[3][0].values()[1]))

        c = i.values()[4]

        # ----------------录入网卡信息--------

        speed = 1000
        ''''''
        idc_name = 'nic_idc_name'
        s = (a, b, speed, c, idc_name, start_ss)

        z.append(s)
    return tuple(z)

def re_st(*incounter):
    start_ss = int(time.time()) - 120

    expire = start_ss - 60
    expire_2 = start_ss - 300

    conn2 = MySQLdb.connect('127.0.0.1', 'root', '123321', 'my_web')
    cur2 = conn2.cursor()

    if incounter:
        #--------------插入nic相关值--此处判断须严格和view里调用输入参数相同
        if incounter[0] == 'net.if.out.bits':
            sql_nic = "insert into  top10_cluster_nic(endpoint,value,speed,counter,idc,add_date)values(%s,%s,%s,%s,%s,%s);"

            sqlnic_2 = "delete  from top10_cluster_nic where add_date < %s" % expire

            tmp_2 = re_nic(start_ss, incounter[0])
            cur2.executemany(sql_nic, tmp_2)
            cur2.execute(sqlnic_2)
            conn2.commit()
        else:
            sql2 = "insert into  top10_end_va_cou(endpoint,value,counter,add_date,cpu_num)values(%s,%s,%s,%s,%s);"

            sql4 = "delete  from top10_end_va_cou where add_date < %s" % expire

            sql5 = "delete  from top10_end_va_cou where add_date < %s" % expire_2

            tmp = re_tu(start_ss, incounter[0])
            if incounter[0] == 'df.statistics.used.percent' or incounter[0] == 'mem.memused.percent':
                cur2.execute(sql5)
            else:
                cur2.execute(sql4)
            cur2.executemany(sql2, tmp)
            conn2.commit()
    else:
        pass
    conn2.close()

'''定时脚本'''

re_st('cpu.idle')
re_st('load.1min')
re_st('df.statistics.used.percent')
re_st('mem.memused.percent')

''''''
re_st('net.if.out.bits')
