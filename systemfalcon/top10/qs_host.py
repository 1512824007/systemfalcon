# -*- coding: utf-8 -*-

import MySQLdb
import os
import time
# Create your views here.
from scrpits import rrdgraph,config

null = float(-1)
end_time = int(time.time()) -60
start_time = end_time - 42600


def re_tu(start, end, host, *incounter):

    endpoint = [ host]
    counters = [incounter[0]]
    res = rrdgraph.graph_query(endpoint,counters, start=start, end=end)
    value_all = list(eval(res))[0].values()[3]
    d_json = []
    if value_all is None:
        pass
    else:
        for i in value_all:
            if i.values()[1] is None:
                tmp = 0
                d_json.append([i.values()[0]*1000, tmp])
            else:
                d_json.append([i.values()[0]*1000, i.values()[1]])
    return d_json


def sf(endpoint, counter, start=start_time, over=end_time):

    def sf_temp(start, over, endpoint, counter, file_ss):
        c = re_tu(start, over, endpoint, counter)
        if counter == 'mem.memused.percent':
            if c == []:
                c_temp = re_tu(start, over, endpoint, 'mem.memfree.percent')
                for i in c_temp:
                    c.append([i[0], 100 - i[1]])
            with open(file_ss, 'w') as c_f:
                c_f.write(str(c))
            return counter
        elif counter == 'cpu.idle':
            c_tem = c
            c = []
            for i in c_tem:
                c.append([i[0], 100 - i[1]])
            with open(file_ss, 'w') as c_f:
                c_f.write(str(c))
            return counter
        elif counter == 'load.1min':
            sql_cpu = "select cpu from device_server where hostname = '%s'" % endpoint
            cpu_num = 1
            c_tem = c
            c = []
            for i in c_tem:
                c.append([i[0], i[1] / cpu_num * 100])
            with open(file_ss, 'w') as c_f:
                c_f.write(str(c))
            return counter
        else:
            with open(file_ss, 'w') as c_f:
                c_f.write(str(c))
            return counter

    file_ss = '/systemfalcon/systemfalcon/static/top10/%s/%s.json' % (counter, endpoint)
    dir_ss = '/systemfalcon/systemfalcon/static/top10/%s/' % counter

    if 'net.if' in counter:
        sql_h_c = "select endpoint_counter.counter from \
        endpoint,endpoint_counter where endpoint.id=endpoint_counter.endpoint_id \
        and endpoint.endpoint = '%s' \
        and endpoint_counter.counter like '%s%%';" % (endpoint, counter)
        conn1 = MySQLdb.connect('{0}'.format(config.DASHBOARD_DB_HOST), 'root', '123321', 'graph')
        cur1 = conn1.cursor()
        cur1.execute(sql_h_c)
        h_c = cur1.fetchall()
        for i in h_c:
            counter = i[0]

            file_ss = '/systemfalcon/systemfalcon/static/top10/%s/%s.json' % (counter, endpoint)
            dir_ss = '/systemfalcon/systemfalcon/static/top10/%s/' % counter
            if not os.path.exists(dir_ss):
                os.makedirs(dir_ss)
            with open(file_ss, 'w') as c_f:
                c_net = re_tu(start, over, endpoint, counter)
                c_f.write(str(c_net))
        return h_c
    elif os.path.exists(file_ss):
        d = sf_temp(start, over, endpoint, counter, file_ss)
        return d
    else:
        if not os.path.exists(dir_ss):
            os.makedirs(dir_ss)
        d = sf_temp(start, over, endpoint, counter, file_ss)
        return d
