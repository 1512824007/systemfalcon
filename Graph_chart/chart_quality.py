#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
import sys
import json
import mysql,mysql_falcon,mysql_oms
from collections import Counter
import rrdgraph_quality
import datetime

db_falcon = mysql_falcon.db_operate()
db= mysql.db_operate()
db_oms = mysql_oms.db_operate()

reload(sys)
sys.setdefaultencoding('utf-8')
sys.getdefaultencoding()

def Chart_quality():
    """网络服务质量"""
    # endpoints = "select b.hostname from idc_idc a ,device_server b where a.id = b.idc_id and a.name={0};".format(args)
    # print endpoints
    # endpoints_hostname = db_oms.select_table(endpoints)
    data = open('./source','w')
    data_dest = open('./source_dest','w')
    for endpoints in open('networksource','r').readlines():
        endpoint = endpoints.strip().split()[1]
        room = endpoints.strip().split()[0]
        # print room
        # endpoint = "sr067.mli-sdjn-01.c4hcdn.cn"
        # NET_TOTAL = ["live.icmp.max/sr001.cnc-hesjz-04=61.55.189.114"]
        f = open('./icmp.txt','r')
        a = {}
        graph_data = []
        graph_data_dest = []

        for i in f.readlines():
            # print i.strip().split()[0],i.split()[1]
            hostname = i.strip().split()[0]

            counter_max = i.strip().split()[1]
            counter_min = i.strip().split()[2]
            counter_avg = i.strip().split()[3]
            # print counter_max,counter_min,counter_avg
            endpoint_counters_max = [{'endpoint': endpoint, 'counter': "{0}".format(counter_max)}]
            endpoint_counters_min = [{'endpoint': endpoint, 'counter': "{0}".format(counter_min)}]
            endpoint_counters_avg = [{'endpoint': endpoint, 'counter': "{0}".format(counter_avg)}]
            # graph_data 从query 取出的单个endpoint的信息（包含数据）
            query_result_max = rrdgraph_quality.graph_query(endpoint_counters_max)
            query_result_min = rrdgraph_quality.graph_query(endpoint_counters_min)
            query_result_avg = rrdgraph_quality.graph_query(endpoint_counters_avg)
            x_max = query_result_max[0]['Values']
            x_min = query_result_min[0]['Values']
            x_avg = query_result_avg[0]['Values']
            # x = query_result[i]
            try:
                xv_max = [int(v["value"]) for v in x_max]
                xv_min = [int(v["value"]) for v in x_min]
                xv_avg = [int(v["value"]) for v in x_avg]
                xv = int((xv_max[0]+xv_min[0]+xv_avg[0])/3)
                # print xv_max,xv_min,xv_avg
                data_dict = {'src_name': u'(源)' + room, 'dest_name': u'(上)' + hostname, 'value': xv}
            except:
                xv=10000
                data_dict = {'src_name':u'(源)'+room,'dest_name':u'(上)'+hostname,'value':xv}
            if xv>0:
                dict_dest = {'name': u'(上)' + hostname, 'value': xv}
                graph_data_dest.append(dict_dest)
            else:
                pass

            graph_data.append(data_dict)

        GD = json.dumps(graph_data)
        GD_dest = json.dumps(graph_data_dest)
        datas = open('./source','a')
        data_dests = open('./source_dest','a')
        datas.write(GD)
        data_dests.write(GD_dest)
        datas.close()
        data_dests.close()

    data_dest.close()
    data.close()

def result():
    f = open('./source','r')
    data = f.readlines()
    json_data =  data[0].replace('][',',')
    datas = open('./results','w')
    f_dest = open('./source_dest', 'r')
    data_dest = f_dest.readlines()
    json_data_dest = data_dest[0].replace('][', ',')
    datas_dest = open('./results_dest', 'w')
    datas.write(json_data)
    datas_dest.write(json_data_dest)
    datas.close()
    datas_dest.close()


if __name__ == '__main__':
    print "start_time:{0}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    Chart_quality()
    result()
    print "end_time:{0}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
