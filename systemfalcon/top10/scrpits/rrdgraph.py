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
START_TIME = END_TIME - 3600
null = float(-1)
def graph_query(endp,counters,start=START_TIME,end=END_TIME):
    user = 'zdl'
    sig = '4329a4b7656f11e89c19000c2971dd94'
    api_token = '{"name":"' + user + '", "sig":"' + sig + '"}'
    directiry="/api/v1/graph/history"
    falcon_header = {
            "Apitoken": api_token,
            "X-Forwarded-For": "127.0.0.1",
            "Content-Type": "application/json",
            "name": user,
            "sig": sig
        }
    params = {
    'url': config.QUERY_ADDR + directiry,
    'headers': falcon_header,
    'timeout': 30
    }

    payload = {
    "step": 60,
    "start_time": start,
    "hostnames": endp,
    "end_time": end,
    "counters": counters,
    "consol_fun": "AVERAGE"
    }
    params['data'] = json.dumps(payload)

    r = requests.post(**params) 
    return r.text
