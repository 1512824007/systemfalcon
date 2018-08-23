# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from django.shortcuts import render,HttpResponse
import config
import time
import requests
import json
import rrdgraph
import mysql_falcon,mysql
from collections import Counter

db_falcon = mysql_falcon.db_operate()
db= mysql.db_operate()

#服务请求数
SERVICES_COUNTERS = ['ss.estab']

S_T = int(time.time())-42600
S_T_before = int(time.time()) - 86400
# Create your views here.

def Chart_SS_Live():
    """各产品服务请求数"""


    endpoints = "select hostname from host where id in (select host_id from grp_host where grp_id=5);"
    endpoints_hostname = db_falcon.select_table(endpoints)
    a = {}

    dict_count0 = Counter(a)
    dict_count1 = Counter(a)

    flow_counters = SERVICES_COUNTERS
    error_t = int(time.time())-3600
    for endpoint in endpoints_hostname:

        endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        query_result = rrdgraph.graph_query(endpoint_counters, start=S_T_before, end=S_T)
        for i in range(0, len(query_result)):
            x = query_result[i]
            try:
                if x["Values"] != None:
                    xv = []
                    num_none = 0
                    for v in x['Values']:

                        if v["value"] == None:
                            num_none +=1
                            s = [v["timestamp"] * 1000.0, 0]
                        else:

                            s = [v["timestamp"] * 1000.0, v["value"]]
                        xv.append(s)
                    if num_none > 30:
                        print x['endpoint']+" has error, it's none_number is "+ str(num_none)
                    else:
                        dict_count0 += Counter(dict(xv))
                else:
                    pass
            except Exception as e:
                print e

        query_result1 = rrdgraph.graph_query(endpoint_counters, start=S_T)
        for i in range(0, len(query_result1)):
            x = query_result1[i]
            try:
                if x["Values"] != None:
                    xv = []
                    for v in x['Values']:

                        if v["value"] == None:
                            s = [v["timestamp"] * 1000.0, 0]
                        else:
                            s = [v["timestamp"] * 1000.0, v["value"]]
                        xv.append(s)
                    dict_count1 += Counter(dict(xv))
                else:
                    pass
            except:
                pass

    dict_count = dict_count0 + dict_count1
    data =  list(sorted(dict_count.items()))
    max_data = max(dict_count.values())
    min_data = min(dict_count.values())

    GD = json.dumps(data)

    f = open('live','w')
    f.write(GD)
    f.close()
    a = open('live_max_min','w')
    a.write(str(max_data)+' '+ str(min_data))
    a.close()

def Chart_SS_Media():
    """各产品服务请求数"""

    endpoints = "select hostname from host where id in (select host_id from grp_host where grp_id=67);"
    endpoints_hostname = db_falcon.select_table(endpoints)
    a = {}
    graph_data = []
    dict_count0 = Counter(a)
    dict_count1 = Counter(a)

    try:
        for endpoint in endpoints_hostname:
            # print endpoint
            # endp = ENDPOINT_LIST[int(endpoint_id)]
            # endpoint = ENDPOINT_LIST[int(endpoint_id)]
            # print endpoint
            flow_counters = SERVICES_COUNTERS

            endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
            # graph_data 从query 取出的单个endpoint的信息（包含数据）
            query_result = rrdgraph.graph_query(endpoint_counters, start=S_T_before, end=S_T)
            for i in range(0, len(query_result)):
                x = query_result[i]
                try:
                    if x["Values"] != None:
                        xv = []
                        num_none = 0
                        for v in x['Values']:

                            if v["value"] == None:
                                num_none += 1
                                s = [v["timestamp"] * 1000.0, 0]
                            else:

                                s = [v["timestamp"] * 1000.0, v["value"]]
                            xv.append(s)
                        if num_none > 30:
                            print x['endpoint']+" has error, it's none_number is "+ str(num_none)
                        else:
                            dict_count0 += Counter(dict(xv))

                    else:
                        pass
                    #xv = [[float(v["timestamp"] * 1000), int(v["value"])] for v in x["Values"]]
                    #dict_count += Counter(dict(xv))
                    # print type(xv)
                except:
                    pass
            query_result1 = rrdgraph.graph_query(endpoint_counters, start=S_T)
            for i in range(0, len(query_result1)):
                x = query_result1[i]
                try:
                    if x["Values"] != None:
                        xv = []
                        for v in x['Values']:

                            if v["value"] == None:
                                s = [v["timestamp"] * 1000.0, 0]
                            else:
                                s = [v["timestamp"] * 1000.0, v["value"]]
                            xv.append(s)
                        dict_count1 += Counter(dict(xv))
                    else:
                        pass
                except:
                    pass

        dict_count = dict_count0 + dict_count1

        xv =  list(dict_count.items())
        data =  list(sorted(dict_count.items()))
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())
        data_dict = {
            "data": xv,
            "name": "Live",
            "cf": 'AVERAGE',
            "endpoint": "Live",
            "counter": "ss.estab",
        }
        graph_data.append(data_dict)
        # print graph_data
        GD = json.dumps(data)
        # live_sql = "insert into openfalcon_rrd_chartlive_ss(json) VALUES ('%s');"%(GD)
        # print live_sql
        # db.mysql_command(live_sql)
        f = open('media','w')
        f.write(GD)
        f.close()
        a = open('media_max_min','w')
        a.write(str(max_data)+' '+ str(min_data))
        a.close()
    except:
        pass

def Chart_SS_Web():
    """各产品服务请求数"""

    endpoints = "select hostname from host where id in (select host_id from grp_host where grp_id=44);"
    endpoints_hostname = db_falcon.select_table(endpoints)
    a = {}

    dict_count0 = Counter(a)
    dict_count1 = Counter(a)
    try:
        for endpoint in endpoints_hostname:

            flow_counters = SERVICES_COUNTERS
            er_c = 0
            endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]

            query_result = rrdgraph.graph_query(endpoint_counters, start=S_T_before, end=S_T)
            for i in range(0, len(query_result)):
                x = query_result[i]
                try:
                    if x["Values"] != None:
                        xv = []
                        num_none = 0
                        for v in x['Values']:

                            if v["value"] == None:
                                num_none += 1
                                s = [v["timestamp"] * 1000.0, 0]
                            else:

                                s = [v["timestamp"] * 1000.0, v["value"]]
                            xv.append(s)
                        if num_none > 30:
                            print x['endpoint'] + " has error, it's none_number is " + str(num_none)
                        else:
                            dict_count0 += Counter(dict(xv))

                    else:
                        pass
                except:
                    pass
            query_result1 = rrdgraph.graph_query(endpoint_counters, start=S_T)
            for i in range(0, len(query_result1)):
                x = query_result1[i]
                try:
                    if x["Values"] != None:
                        xv = []
                        for v in x['Values']:

                            if v["value"] == None:
                                s = [v["timestamp"] * 1000.0, 0]
                            else:
                                s = [v["timestamp"] * 1000.0, v["value"]]
                            xv.append(s)
                        dict_count1 += Counter(dict(xv))
                    else:
                        pass
                except:
                    pass

        dict_count = dict_count0 + dict_count1

        data =  list(sorted(dict_count.items()))
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())

        GD = json.dumps(data)

        f = open('web','w')
        f.write(GD)
        f.close()
        a = open('web__max_min','w')
        a.write(str(max_data)+' '+ str(min_data))
        a.close()
    except:
        pass


if __name__ == '__main__':
    Chart_SS_Live()
    Chart_SS_Media()
    Chart_SS_Web()

