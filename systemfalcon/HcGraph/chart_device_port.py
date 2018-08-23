#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import unicode_literals

import json
import sys
from collections import Counter

import mysql
from top10 import mysql_falcon
from HcGraph import rrdgraph,rrdgraphlast

db_falcon = mysql_falcon.db_operate()
db= mysql.db_operate()

reload(sys)
sys.setdefaultencoding('utf-8')
sys.getdefaultencoding()


def Chart_Room(endpoint,counter):
    """各产品服务请求数"""
    PORT = ["net.port.listen/{0}".format(counter)]
    graph_data = []
    flow_counters = PORT
    # print flow_counters
    endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
    # graph_data 从query 取出的单个endpoint的信息（包含数据）
    query_result = rrdgraphlast.graph_query(endpoint_counters)
    try:
        for i in range(0, len(query_result)):
            x = query_result[i]
            xv = [(v["value"]) for v in x["Values"]]
            graph_data.append(xv)
        GD = json.dumps(graph_data)
        return GD
    except:
        pass

# if __name__ == '__main__':
#     Chart_Room()
