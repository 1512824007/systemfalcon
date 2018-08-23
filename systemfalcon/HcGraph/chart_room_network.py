#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import unicode_literals
import os
import json
import mysql
from openfalcon import mysql_falcon
from collections import Counter
import rrdgraph
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

db_falcon = mysql_falcon.db_operate()

db = mysql.db_operate()



def Chart_Network_Live(args):
    """机房直播设备质量"""

    if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/live/room'.format(args)):
        if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/live/'.format(args)):
            os.makedirs('/systemfalcon/systemfalcon/static/alarm/{0}/live/'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/live/room'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/live/room_max_min'.format(args))
    endpoints_hostname = [['livehostname1','livehostname2']]
    a = {}
    graph_data = []
    dict_count = Counter(a)
    for endpoint in endpoints_hostname:
        NET_OUT_Other = ["net.if.out.bits/iface={0}".format('ens33')]

        endpoint_counters = [ endpoint]
        try:
            query_result = rrdgraph.graph_query(endpoint_counters,NET_OUT_Other)
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
                    dict_count += Counter(dict(xv))

        except Exception as e:
            print (e)


    data =  list(sorted(dict_count.items()))
    GD = json.dumps(data)

    f = open('/systemfalcon/systemfalcon/static/alarm/{0}/live/room'.format(args), 'w')
    #f = open('/systemfalcon/static/alarm/{0}/live/room'.format(args), 'w')
    f.write(GD)
    f.close()
    try:
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())

        a = open('/systemfalcon/systemfalcon/static/alarm/{0}/live/room_max_min'.format(args), 'w')
        #a = open('/systemfalcon/static/alarm/{0}/live/room_max_min'.format(args),'w')

        a.write(str(max_data)+' '+ str(min_data))
        a.close()
    except Exception as e:
        pass



def Chart_Network_Media(args):
    """点播网络流量"""
    endpoints_hostname = [['mediahost1','mediahost2']]
    a = {}

    graph_data = []
    dict_count = Counter(a)

    if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/media/room'.format(args)):
        if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/media/'.format(args)):
            os.makedirs('/systemfalcon/systemfalcon/static/alarm/{0}/media/'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/media/room'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/media/room_max_min'.format(args))

    for endpoint in endpoints_hostname:
        NET_OUT_Other = ["net.if.out.bits/iface={0}".format('ens33')]
        endpoint_counters = [endpoint]
        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        try:
            query_result = rrdgraph.graph_query(endpoint_counters,NET_OUT_Other)
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
                    dict_count += Counter(dict(xv))
        except Exception as e:
            pass
    data =  list(sorted(dict_count.items()))
    GD = json.dumps(data)

    f = open('/systemfalcon/systemfalcon/static/alarm/{0}/media/room'.format(args), 'w')
    #f = open('/systemfalcon/static/alarm/{0}/media/room'.format(args), 'w')

    f.write(GD)
    f.close()
    try:
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())

        a = open('./static/alarm/{0}/media/room_max_min'.format(args), 'w')
        #a = open('/systemfalcon/static/alarm/{0}/media/room_max_min'.format(args),'w')

        a.write(str(max_data)+' '+ str(min_data))
        a.close()
    except Exception as e:
        pass


def Chart_Network_Web(args):
    """WEB页面网络流量"""
    #         and i.`name` in('GsWeb-页面平台专用','页面缓存服务','页面加速')
    endpoints_hostname = [['webhost1','webhost2']]
    a = {}
    graph_data = []

    dict_count = Counter(a)

    if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/web/room'.format(args)):
        if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/web/'.format(args)):
            os.makedirs('/systemfalcon/systemfalcon/static/alarm/{0}/web/'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/web/room'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/web/room_max_min'.format(args))

    for endpoint in endpoints_hostname:
        NET_OUT_Other = ["net.if.out.bits/iface={0}".format('ens33')]

        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        try:
            query_result = rrdgraph.graph_query(endpoint,NET_OUT_Other)
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
                    dict_count += Counter(dict(xv))
        except Exception as e:
            print (e)

    data =  list(sorted(dict_count.items()))
    GD = json.dumps(data)

    f = open('/systemfalcon/systemfalcon/static/alarm/{0}/web/room'.format(args), 'w')
    #f = open('/systemfalcon/static/alarm/{0}/web/room'.format(args), 'w')

    f.write(GD)
    f.close()
    try:
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())

        a = open('/systemfalcon/systemfalcon/static/alarm/{0}/web/room_max_min'.format(args), 'w')
        #a = open('/systemfalcon/static/alarm/{0}/web/room_max_min'.format(args), 'w')

        a.write(str(max_data) + ' ' + str(min_data))
        a.close()
    except Exception as e:
        pass

