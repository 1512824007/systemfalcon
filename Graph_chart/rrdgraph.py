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

import config

END_TIME = int(time.time()) - 60
START_TIME = END_TIME - 86400

def graph_query(endpoint_counters,cf='AVERAGE',start=START_TIME,end=END_TIME):

    params = {
        "start":start,
        "end":end,
        "cf":cf,
        "endpoint_counters":endpoint_counters,
    }
    r = requests.post("%s/graph/history" %config.QUERY_ADDR,data=json.dumps(params))
    if r.status_code != 200:
        raise Exception("{} : {}".format(r.status_code,r.text))
    return r.json()
