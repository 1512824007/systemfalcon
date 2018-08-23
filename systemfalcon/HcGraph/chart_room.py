#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import unicode_literals
import sys
import json
import mysql

from top10 import mysql_falcon
from collections import Counter
import rrdgraph
import os
db_falcon = mysql_falcon.db_operate()
db= mysql.db_operate()


reload(sys)
sys.setdefaultencoding('utf-8')
sys.getdefaultencoding()


def Chart_Room(args):
    """各产品服务请求数"""

    if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/'.format(args)):
        os.makedirs('/systemfalcon/systemfalcon/static/alarm/{0}/'.format(args))
    else:
        if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/room'.format(args)):
            os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/room'.format(args))
        if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/room_max_min'.format(args)):
            os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/room_max_min'.format(args))

    endpoints = "select b.hostname from idc_idc a ,device_server b where a.id = b.idc_id and a.name='{0}';".format(args)
    # print endpoints
    endpoints_hostname = ['endpoints_hostnam1','endpoints_hostnam2'] 
    endpoints_ldc = ['endpoints_ldc1','endpoints_ldc2']

    a = {}
    graph_data = []
    dict_count = Counter(a)
    ldc_count = Counter(a)

    for endpoint in endpoints_hostname:
        NET_OUT_Other = ["net.if.out.bits/iface={0}".format('ens33')]
        endpoints = [endpoint]
        try:
            query_result = rrdgraph.graph_query(endpoints,NET_OUT_Other)
            print(query_result)
            for i in range(0, len(query_result)):
                x = query_result[i]
                try:
                    if x["Values"] != None:
                        xv = []
                        for v in x['Values']:
                            if v["value"] == None:
                                s = [v["timestamp"] * 1000.0, 0]
                            else:
                                s = [v["timestamp"] * 1000.0, v["value"]]
                            xv.append(s)
                        dict_count += Counter(dict(xv))
                    else:
                        pass
                except Exception as e:
                    #print e
                    pass
        except Exception as e:
            pass
    for ldc in endpoints_ldc:

        NET_OUT_LDC = ["net.if.out.bits/iface={0}".format('ens33')]

        endpoint_counters = [ldc]
        try:
            query_result = rrdgraph.graph_query(endpoint_counters,NET_OUT_LDC)
            for i in range(0, len(query_result)):
                x = query_result[i]
                if x["Values"] != None:
                    xv = []
                    for v in x['Values']:
                        if v["value"] == None:
                            s = [v["timestamp"] * 1000.0, 0]
                        else:
                            s = [v["timestamp"] * 1000.0, v["value"]]
                        xv.append(s)
                    ldc_count += Counter(dict(xv))
                else:
                    pass
        except Exception as e:
            pass
    count = Counter(dict(dict_count))+Counter(dict(ldc_count))

    sort = list(sorted(count.items()))
    sort = json.dumps(sort)
    f = open('/systemfalcon/systemfalcon/static/alarm/{0}/room'.format(args), 'w')

    f.write(sort)
    f.close()
    try:
        a = open('/systemfalcon/systemfalcon/static/alarm/{0}/room_max_min'.format(args), 'w')
        max_data = max(count.values())
        min_data = min(count.values())

        a.write(str(max_data)+' '+ str(min_data))
        a.close()
    except  Exception as e:
        pass

