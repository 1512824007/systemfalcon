#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import unicode_literals
import os
import json
import mysql
import mysql_falcon
from collections import Counter
import rrdgraph
import time
db_falcon = mysql_falcon.db_operate()
db = mysql.db_operate()
S_T = int(time.time())-42600
S_T_before = int(time.time()) - 86400

def Chart_Network_Live():
    if not os.path.exists('net_live'):
        os.system('touch ' + 'net_live')
    if not os.path.exists('net_live_max_min'):
        os.system('touch ' + 'net_live_max_min')
    endpoints = "select hostname from host where id in (select host_id from grp_host where grp_id=5);"
    endpoints_hostname = db_falcon.select_table(endpoints)
    a = {}

    dict_count0 = Counter(a)
    dict_count1 = Counter(a)
    for endpoint in endpoints_hostname:
        NET_OUT = ["net.if.out.bits/iface={0}".format('ens33')]

        flow_counters = NET_OUT

        endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        try:
            query_result = rrdgraph.graph_query(endpoint_counters, start=S_T_before, end=S_T)
            for i in range(0, len(query_result)):
                x = query_result[i]
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
        except Exception as e:
            pass
        try:
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
        except Exception as e:
            pass
    dict_count = dict_count0 + dict_count1
    data = list(sorted(dict_count.items()))
    GD = json.dumps(data)
    f = open('net_live', 'w')

    f.write(GD)
    f.close()
    try:
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())
        a = open('net_live_max_min', 'w')
        a.write(str(max_data) + ' ' + str(min_data))
        a.close()
    except Exception as e:
        pass


def Chart_Network_Media():
    if not os.path.exists('net_media'):
        os.system('touch ' + 'net_media')
    if not os.path.exists('net_media_max_min'):
        os.system('touch ' + 'net_media_max_min')

    endpoints = "select hostname from host where id in (select host_id from grp_host where grp_id=67);"
    endpoints_hostname = db_falcon.select_table(endpoints)
    a = {}

    dict_count0 = Counter(a)
    dict_count1 = Counter(a)

    NET_OUT = ["net.if.out.bits/iface={0}".format('ens33')]
    for endpoint in endpoints_hostname:

        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        try:
            query_result = rrdgraph.graph_query([endpoint],NET_OUT, start=S_T_before, end=S_T)
            for i in range(0, len(query_result)):
                x = query_result[i]
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
        except Exception as e:
            pass
        try:
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
        except Exception as e:
            pass
    dict_count = dict_count0 + dict_count1
    data = list(sorted(dict_count.items()))
    GD = json.dumps(data)
    f = open('net_media', 'w')
    f.write(GD)
    f.close()
    try:
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())
        a = open('net_media_max_min', 'w')
        a.write(str(max_data) + ' ' + str(min_data))
        a.close()
    except Exception as e:
        pass


def Chart_Network_Web():
    """各产品服务请求数"""
    if not os.path.exists('net_web'):
        os.system('touch ' + 'net_web')
    if not os.path.exists('net_web_max_min'):
        os.system('touch ' + 'net_web_max_min')
    endpoints = "select hostname from host where id in (select host_id from grp_host where grp_id=44);"
    endpoints_hostname = db_falcon.select_table(endpoints)
    a = {}
    graph_data = []
    dict_count0 = Counter(a)
    dict_count1 = Counter(a)
    NET_OUT = ["net.if.out.bits/iface={0}".format('ens33')]
    for endpoint in endpoints_hostname:

        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        try:
            query_result = rrdgraph.graph_query([endpoint],NET_OUT, start=S_T_before, end=S_T)
            for i in range(0, len(query_result)):
                x = query_result[i]
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
        except Exception as e:
            pass
        try:
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
        except Exception as e:
            pass
    dict_count = dict_count0 + dict_count1
    data = list(sorted(dict_count.items()))
    GD = json.dumps(data)
    f = open('net_web', 'w')

    f.write(GD)
    f.close()
    try:
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())
        a = open('net_web_max_min', 'w')

        a.write(str(max_data) + ' ' + str(min_data))
        a.close()
    except Exception as e:
        pass

if __name__ == '__main__':

    Chart_Network_Live()
    Chart_Network_Media()
    Chart_Network_Web()
