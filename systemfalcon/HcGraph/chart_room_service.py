#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import unicode_literals
import os
import json
import mysql
from top10 import mysql_falcon
from collections import Counter
import rrdgraph
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
sys.getdefaultencoding()

db_falcon = mysql_falcon.db_operate()
db= mysql.db_operate()

NET_TOTAL=["ss.estab"]
NET_TOTAL_MEDIA=["ss.estab"]
NET_TOTAL_WEB=["ss.estab"]

def Chart_Network_Live(args):
    """机房直播设备质量"""

    print u"机房直播设备并发数"

    if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/live/room_service_live'.format(args)):
        if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/live/'.format(args)):
            os.makedirs('/systemfalcon/systemfalcon/static/alarm/{0}/live/'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/live/room_service_live'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/live/room_service_live_max_min'.format(args))
    endpoints = """
        select DISTINCT f.hostname from 
        idc_idc a ,
        idc_idcnetwork b,
        idc_netline d,
        idc_idcnetline e,
        device_server f,
        business_clusterserver g,
        business_cluster h,
        business_project i
         where 
         a.id=b.idc_id 
         and b.idc_id=e.idc_id 
         and b.netline_id=e.id
         and d.id = e.netline_id 
         and a.id = e.idc_id
         and a.id = f.idc_id
         and g.device_id = f.id and g.cluster_id=h.id and h.project_id=i.id and d.`name` not in('IPMI','内网') 
         and i.`name` in('直播视频加速','直播源站(北京)','直播302调度集群','直播新版本测试集群')
         and a.name='{0}';""".format(args)

    #print endpoints
    endpoints_hostname = ['livehost1','livehost2'] 
    a = {}
    graph_data = []
    dict_count = Counter(a)
    try:
        for endpoint in endpoints_hostname:
            flow_counters = NET_TOTAL

            endpoint_counters = [endpoint,]
            # graph_data 从query 取出的单个endpoint的信息（包含数据）
            query_result = rrdgraph.graph_query(endpoint_counters,NET_TOTAL)
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

                    #xv = [[float(v["timestamp"] * 1000), int(v["value"])] for v in x["Values"]]
                    #dict_count += Counter(dict(xv))
                    # print type(xv)
                except:
                    pass
            # print type(graph_data)
        xv =  list(dict_count.items())
        data =  list(sorted(dict_count.items()))
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())
        data_dict = {
            "data": xv,
            "name": "Net_Live",
            "cf": 'AVERAGE',
            "endpoint": "Net_Live",
            "counter": "net.if.total.bits/iface=bond0",
        }
        graph_data.append(data_dict)
        # print graph_data
        GD = json.dumps(data)
        print GD

        f = open('/systemfalcon/systemfalcon/static/alarm/{0}/live/room_service_live'.format(args),'w')
        f.write(GD)
        f.close()
        a = open('/systemfalcon/systemfalcon/static/alarm/{0}/live/room_service_live_max_min'.format(args),'w')

        a.write(str(max_data)+' '+ str(min_data))
        a.close()
    except:
        pass

def Chart_Network_Media(args):
    """点播网络流量"""

    print u"机房点播设备并发数"

    if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/media/room_service_media'.format(args)):
        if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/media/'.format(args)):
            os.makedirs('/systemfalcon/systemfalcon/static/alarm/{0}/media/'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/media/room_service_media'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/media/room_service_media_max_min'.format(args))
    endpoints_hostname = ['meiadhost1','mediahost2']
    a = {}

    graph_data = []
    dict_count = Counter(a)
    try:
        for endpoint in endpoints_hostname:
            flow_counters = NET_TOTAL

            endpoint_counters = [endpoint]
            # graph_data 从query 取出的单个endpoint的信息（包含数据）

            query_result = rrdgraph.graph_query(endpoint_counters,flow_counters)
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


                    #xv = [[float(v["timestamp"] * 1000), int(v["value"])] for v in x["Values"]]
                    #dict_count += Counter(dict(xv))
                    # print type(xv)
                except:
                    pass
            # print type(graph_data)
        xv =  list(dict_count.items())
        data =  list(sorted(dict_count.items()))
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())
        data_dict = {
            "data": xv,
            "name": "Net_Media",
            "cf": 'AVERAGE',
            "endpoint": "Net_Media",
            "counter": "net.if.total.bits/iface=bond0",
        }
        graph_data.append(data_dict)
        # print graph_data
        GD = json.dumps(data)
        # live_sql = "insert into openfalcon_rrd_chartlive_ss(json) VALUES ('%s');"%(GD)
        # print live_sql
        # db.mysql_command(live_sql)
        #f = open('./static/alarm/room_service_media','w')

        f = open('/systemfalcon/systemfalcon/static/alarm/{0}/media/room_service_media'.format(args),'w')
        f.write(GD)
        f.close()
        a = open('/systemfalcon/systemfalcon/static/alarm/{0}/media/room_service_media_max_min'.format(args),'w')

        a.write(str(max_data)+' '+ str(min_data))
        a.close()
    except:
        pass

def Chart_Network_Web(args):
    """WEB页面网络流量"""
    print u"机房页面设备并发数"

    if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/web/room_service_web'.format(args)):
        if not os.path.exists('/systemfalcon/systemfalcon/static/alarm/{0}/web/'.format(args)):
            os.makedirs('/systemfalcon/systemfalcon/static/alarm/{0}/web/'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/web/room_service_web'.format(args))
        os.system('touch ' + '/systemfalcon/systemfalcon/static/alarm/{0}/web/room_service_web_max_min'.format(args))
    endpoints_hostname = ['webhost1','webhost2'] 
    a = {}
    graph_data = []
    dict_count = Counter(a)
    try:
        for endpoint in endpoints_hostname:

            flow_counters = NET_TOTAL

            endpoint_counters = [endpoint]
            # graph_data 从query 取出的单个endpoint的信息（包含数据）
            query_result = rrdgraph.graph_query(endpoint_counters,flow_counters)
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

                except:
                    pass
            # print type(graph_data)
        xv =  list(dict_count.items())
        data =  list(sorted(dict_count.items()))
        max_data = max(dict_count.values())
        min_data = min(dict_count.values())
        data_dict = {
            "data": xv,
            "name": "Net_Web",
            "cf": 'AVERAGE',
            "endpoint": "Net_Web",
            "counter": "net.if.total.bits/iface=bond0",
        }
        graph_data.append(data_dict)
        # print graph_data
        GD = json.dumps(data)
        # live_sql = "insert into openfalcon_rrd_chartlive_ss(json) VALUES ('%s');"%(GD)
        # print live_sql
        # db.mysql_command(live_sql)
        #f = open('./static/alarm/room_service_web','w')
        f = open('/systemfalcon/systemfalcon/static/alarm/{0}/web/room_service_web'.format(args), 'w')
        f.write(GD)
        f.close()
        a = open('/systemfalcon/systemfalcon/static/alarm/{0}/web/room_service_web_max_min'.format(args),'w')
        #a = open('./static/alarm/room_service_web_max_min','w')

        a.write(str(max_data)+' '+ str(min_data))
        a.close()
    except:
        pass


