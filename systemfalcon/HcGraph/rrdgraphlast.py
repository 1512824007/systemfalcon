#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-5-24 下午8:34
# @Author  : jinxin
# @Site    : 
# @File    : rrdgraph.py.py
# @Software: PyCharm
import requests

import json

import time

from top10 import config
#
# def graph_query(endpoint,counter):
#     '''
#     #!/bin/bash
#     if [ $# != 2 ];then
#         printf "format:./last \"endpoint\" \"counter\"\n"
#         exit 1
#     fi
#
#     # args
#     endpoint=$1
#     counter=$2
#
#     # form request body
#     req="[{\"endpoint\":\"$endpoint\", \"counter\":\"$counter\"}]"
#
#     # request
#     url="http://127.0.0.1:9966/graph/last"
#     curl -s -X POST -d "$req" "$url" | python -m json.tool
#     '''
#     req = [{"endpoint":endpoint, "counter":counter}]
#     r = requests.post("%s/graph/last"% HcGraph.config.QUERY_ADDR,json.dumps(req))
#     if r.status_code != 200:
#         raise Exception("{} : {}".format(r.status_code,r.text))
#     return r.json()

def graph_query(endpoint_counters,cf='AVERAGE'):
    END_TIME = int(time.time())
    # print END_TIME
    # print u"时间戳"
    START_TIME = END_TIME - 60
    start = START_TIME
    end = END_TIME

    '''
    params:
        [
                {
                    "endpoint": "xx",
                    "counter": "load.1min",
                },
                {
                    "endpoint": "yy",
                    "counter": "cpu.idle",
                },
        ]

    return:
        [
            {
                "Filename": "/home/work/data/6070/79/794a6adefed6b10550b4aaaf4c10d20c_GAUGE_60.rrd",
                "addr": "graph1:6070",
                "consolFuc": "GAUGE",
                "counter": "load.1min",
                "endpoint": "xx",
                "step": 60
            },
            {
                "Filename": "/home/work/data/6070/3c/3cb8b78377824b867c6324463ac736b6_GAUGE_60.rrd",
                "addr": "graph2:6070",
                "consolFuc": "GAUGE",
                "counter": "cpu.idle",
                "endpoint": "yy",
                "step": 60
            }
        ]
    '''
    params = {
        "start":start,
        "end":end,
        "cf":cf,
        "endpoint_counters":endpoint_counters,
    }
    r = requests.post("%s/graph/history" % config.QUERY_ADDR, data=json.dumps(params))
    if r.status_code != 200:
        raise Exception("{} : {}".format(r.status_code,r.text))
    return r.json()