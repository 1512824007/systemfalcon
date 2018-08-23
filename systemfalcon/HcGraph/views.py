# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import json
from HcGraph.util import rrdgraph
from openfalcon import mysql_falcon
import chart_room_network, chart_room_service

db_falcon = mysql_falcon.db_operate()

ENDPOINT_LIST = ['sr004.cnc-gdmz-01.c4hcdn.cn',
                 'sr001.cm-jswx-01.c4hcdn.cn',
                 'sr001.ct-ahbb-01.c4hcdn.cn',
                 'sr002.cm-gddg-01.c4hcdn.cn',
                 'sr002.cnc-zjhz-03.c4hcdn.cn',
                 'sr003.cm-shsh-01.c4hcdn.cn',
                 'sr004.cer-hbwh-01.c4hcdn.cn',
                 'sr005.cm-gdgz-04.c4hcdn.cn',
                 'sr006.cm-gxnn-01.c4hcdn.cn',
                 'sr008.gwb-gdgz-01.c4hcdn.cn',
                 ]

FLOW_COUNTERS = ['net.if.in.bits/iface=br0','net.if.out.bits/iface=br0']

#服务请求数
SERVICES_COUNTERS = ['ss.estab']
root_dir = '/systemfalcon'

# Create your views here.

def index(request):

    SysEndpoint_list = sorted(ENDPOINT_LIST)
    counters = FLOW_COUNTERS

    return render(request,'view/chart.html',locals())


def Chart_Big(request,endpoint_id):
    """节点流量"""
    if request.method == 'GET':

        endp = ENDPOINT_LIST[int(endpoint_id)]
        endpoint = ENDPOINT_LIST[int(endpoint_id)]
        flow_counters = FLOW_COUNTERS

        endpoint_counters = [{'endpoint':endpoint,'counter':i} for i in flow_counters]
        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        query_result = rrdgraph.graph_query(endpoint_counters)
        #print graph_data
        graph_data = []

        for i in range(0,len(query_result)):
            x = query_result[i]
            try:
                xv = [[float(v["timestamp"]*1000), v["value"]] for v in x["Values"]]
                #print xv
                data_dict = {
                            "data": xv,
                            "name": query_result[i]["endpoint"],
                            "cf": 'AVERAGE',
                            "endpoint": query_result[i]["endpoint"],
                            "counter": query_result[i]["counter"],
                }
                graph_data.append(data_dict)
                # print graph_data
            except:
                pass
        GD = json.dumps(graph_data)
        # print type(graph_data)
    return render(request,'view/chart_big.html',locals())

def Chart_live(request):
    graph_data = open('{0}/Graph_chart/live'.format(root_dir),'r').readline()
    max_data = open('{0}/Graph_chart/live_max_min'.format(root_dir),'r').readline().split()[0]
    min_data = open('{0}/Graph_chart/live_max_min'.format(root_dir),'r').readline().split()[1]
    return render(request,'view/chart_ss.html',{'graph_data':graph_data,'max_data':max_data,'min_data':min_data})

def Chart_media(request):
    graph_data = open('{0}/Graph_chart/media'.format(root_dir),'r').readline()
    max_data = open('{0}/Graph_chart/media_max_min'.format(root_dir),'r').readline().split()[0]
    min_data = open('{0}/Graph_chart/media_max_min'.format(root_dir),'r').readline().split()[1]
    return render(request,'view/chart_ss_media.html',{'graph_data':graph_data,'max_data':max_data,'min_data':min_data})
"""拓扑网络质量读取数据"""
def Chart_web(request):
    graph_data = open('{0}/Graph_chart/web'.format(root_dir),'r').readline()
    max_data = open('{0}/Graph_chart/web__max_min'.format(root_dir),'r').readline().split()[0]
    min_data = open('{0}/Graph_chart/web__max_min'.format(root_dir),'r').readline().split()[1]
    return render(request,'view/chart_ss_web.html',{'graph_data':graph_data,'max_data':max_data,'min_data':min_data})


def Chart_live_net(request):
    graph_data = open('{0}/Graph_chart/net_live'.format(root_dir),'r').readline()
    max_data = open('{0}/Graph_chart/net_live_max_min'.format(root_dir),'r').readline().split()[0]
    min_data = open('{0}/Graph_chart/net_live_max_min'.format(root_dir),'r').readline().split()[1]
    return render(request,'view/chart_net.html',{'graph_data':graph_data,'max_data':max_data,'min_data':min_data})

def Chart_media_net(request):
    graph_data = open('{0}/Graph_chart/net_media'.format(root_dir),'r').readline()
    max_data = open('{0}/Graph_chart/net_media_max_min'.format(root_dir),'r').readline().split()[0]
    min_data = open('{0}/Graph_chart/net_media_max_min'.format(root_dir),'r').readline().split()[1]
    return render(request,'view/chart_net_media.html',{'graph_data':graph_data,'max_data':max_data,'min_data':min_data})

def Chart_web_net(request):
    graph_data = open('{0}/Graph_chart/net_web'.format(root_dir),'r').readline()
    max_data = open('{0}/Graph_chart/net_web_max_min'.format(root_dir),'r').readline().split()[0]
    min_data = open('{0}/Graph_chart/net_web_max_min'.format(root_dir),'r').readline().split()[1]
    return render(request,'view/chart_net_web.html',{'graph_data':graph_data,'max_data':max_data,'min_data':min_data})



def Chart_room_live(request,roomname):
    chart_room_network.Chart_Network_Live(roomname)
    graph_data = open('{1}/systemfalcon/static/alarm/{0}/live/room'.format(roomname,root_dir),'r').readline()
    m = open('{1}/systemfalcon/static/alarm/{0}/live/room_max_min'.format(roomname,root_dir), 'r').readline()
    if m == '':
        max_data = ''
        min_data = ''
    else:
        max_data = m.split()[0]
        min_data = m.split()[1]

    return render(request, 'view/chart_room_live.html', {'graph_data':graph_data, 'max_data':max_data, 'min_data':min_data})

def Chart_room_media(request,roomname):
    chart_room_network.Chart_Network_Media(roomname)
    graph_data = open('{1}/systemfalcon/static/alarm/{0}/media/room'.format(roomname,root_dir),'r').readline()
    m = open('{1}/systemfalcon/static/alarm/{0}/media/room_max_min'.format(roomname,root_dir), 'r').readline()

    if m == '':
        max_data = ''
        min_data = ''
    else:
        max_data = m.split()[0]
        min_data = m.split()[1]

    return render(request, 'view/chart_room_media.html', {'graph_data':graph_data, 'max_data':max_data, 'min_data':min_data})


def Chart_room_web(request,roomname):
    chart_room_network.Chart_Network_Web(roomname)
    graph_data = open('{1}/systemfalcon/static/alarm/{0}/web/room'.format(roomname,root_dir),'r').readline()
    m = open('{1}/systemfalcon/static/alarm/{0}/web/room_max_min'.format(roomname,root_dir), 'r').readline()

    if m == '':
        max_data = ''
        min_data = ''
    else:
        max_data = m.split()[0]
        min_data = m.split()[1]

    return render(request, 'view/chart_room_web.html', {'graph_data':graph_data, 'max_data':max_data, 'min_data':min_data})



"""单机房并发数"""
def Chart_room_live_ss(request,roomname):
    chart_room_service.Chart_Network_Live(roomname)
    graph_data = open('{1}/systemfalcon/static/alarm/{0}/live/room_service_live'.format(roomname,root_dir), 'r').readline()
    m = open('{1}/systemfalcon/static/alarm/{0}/live/room_service_live_max_min'.format(roomname,root_dir), 'r').readline()
    if m == '':
        max_data = ''
        min_data = ''
    else:
        max_data = m.split()[0]
        min_data = m.split()[1]
    return render(request, 'view/room/chart_room_ss_live.html', {'graph_data':graph_data, 'max_data':max_data, 'min_data':min_data})

def Chart_room_media_ss(request,roomname):
    chart_room_service.Chart_Network_Media(roomname)
    graph_data = open('{1}/systemfalcon/static/alarm/{0}/media/room_service_media'.format(roomname,root_dir), 'r').readline()
    m = open('{1}/systemfalcon/static/alarm/{0}/media/room_service_media_max_min'.format(roomname,root_dir), 'r').readline()
    if m == '':
        max_data = ''
        min_data = ''
    else:
        max_data = m.split()[0]
        min_data = m.split()[1]
    return render(request, 'view/room/chart_room_ss_media.html', {'graph_data':graph_data, 'max_data':max_data, 'min_data':min_data})


def Chart_room_web_ss(request,roomname):
    chart_room_service.Chart_Network_Web(roomname)
    graph_data = open('{1}/systemfalcon/static/alarm/{0}/web/room_service_web'.format(roomname,root_dir), 'r').readline()
    m = open('{1}/systemfalcon/static/alarm/{0}/web/room_service_web_max_min'.format(roomname,root_dir), 'r').readline()
    if m == '':
        max_data = ''
        min_data = ''
    else:
        max_data = m.split()[0]
        min_data = m.split()[1]
    return render(request, 'view/room/chart_room_ss_web.html', {'graph_data':graph_data, 'max_data':max_data, 'min_data':min_data})


def Chart_net_index(request):
    """拓扑网络质量"""
    return render(request,'view/chart_net_index.html',locals())

def Chart_ss_index(request):
    """服务连接数"""
    return render(request,'view/chart_ss_index.html',locals())


def Chart_room_index(request, roomname):
    """单个机房网络质量"""
    return render(request,'view/chart_room_index.html',{"roomname": roomname})

def Chart_room_index_ss(request, roomname):
    """单机房并发数"""
    return render(request,'view/room/chart_room_ss_index.html',{"roomname": roomname})


def Chart_Server_load(request,endpoint):
    """故障设备负载"""
    if request.method == 'GET':
        NET_TOTAL = ["load.1min", "load.5min", "load.15min"]
        # endpoint="sr006.ct-zjhz-04.c4hcdn.cn"
        graph_data = []
        try:
            flow_counters = NET_TOTAL
            endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
            # graph_data 从query 取出的单个endpoint的信息（包含数据）
            query_result = rrdgraph.graph_query(endpoint_counters)
            # print len(query_result)
            for i in range(0, len(query_result)):
                x = query_result[i]
                # print x
                try:
                    xv = [[float(v["timestamp"] * 1000), (v["value"])] for v in x["Values"]]
                    data_dict = {
                        "data": xv,
                        "name": "设备负载",
                        "cf": 'AVERAGE',
                        "endpoint": endpoint,
                        "counter": query_result[i]['counter'],
                    }
                    graph_data.append(data_dict)
                    # print graph_data
                except:
                    pass
            GD = json.dumps(graph_data)
        except:
            pass

    return render(request,'view/alarm/chart_server_load.html',locals())

def Chart_Server_cpu(request,endpoint):
    """故障设备CPU使用负载"""
    if request.method == 'GET':
        NET_TOTAL = ["cpu.user","cpu.system","cpu.iowait"]
        # endpoint="sr006.ct-zjhz-04.c4hcdn.cn"
        graph_data = []
        try:
            flow_counters = NET_TOTAL
            endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
            # graph_data 从query 取出的单个endpoint的信息（包含数据）
            query_result = rrdgraph.graph_query(endpoint_counters)
            # print len(query_result)
            for i in range(0, len(query_result)):
                x = query_result[i]
                # print x
                try:
                    xv = [[float(v["timestamp"] * 1000), (v["value"])] for v in x["Values"]]
                    data_dict = {
                        "data": xv,
                        "name": "设备负载",
                        "cf": 'AVERAGE',
                        "endpoint": endpoint,
                        "counter": query_result[i]['counter'],
                    }
                    graph_data.append(data_dict)
                    # print graph_data
                except:
                    pass
            GD = json.dumps(graph_data)
        except:
            pass

    return render(request,'view/alarm/chart_server_cpu.html',locals())

def Chart_Server_mem(request,endpoint):
    """故障设备内存使用占比"""
    if request.method == 'GET':
        NET_TOTAL = ["mem.memfree.percent"]
        # endpoint="sr006.ct-zjhz-04.c4hcdn.cn"
        graph_data = []
        try:
            flow_counters = NET_TOTAL
            endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
            # graph_data 从query 取出的单个endpoint的信息（包含数据）
            query_result = rrdgraph.graph_query(endpoint_counters)
            # print len(query_result)
            for i in range(0, len(query_result)):
                x = query_result[i]
                # print x
                try:
                    xv = [[float(v["timestamp"] * 1000), (v["value"])] for v in x["Values"]]
                    data_dict = {
                        "data": xv,
                        "name": "设备负载",
                        "cf": 'AVERAGE',
                        "endpoint": endpoint,
                        "counter": query_result[i]['counter'],
                    }
                    graph_data.append(data_dict)
                    # print graph_data
                except:
                    pass
            GD = json.dumps(graph_data)
        except:
            pass

    return render(request,'view/alarm/chart_server_memory.html',locals())


def Chart_Server_network(request,endpoint):
    """故障设备网卡流量变化"""
    if request.method == 'GET':
        """设备服务端口及状态"""
        openfalcon_sql = """
                select c.grp_name from `host` a,grp_host b ,grp c  where a.id=b.host_id 
                and b.grp_id=c.id and a.hostname='%s';""" % (endpoint)
        openfalcon = db_falcon.mysql_command(openfalcon_sql)

        a = [grp_name[0] for grp_name in openfalcon]
        # print ''.join(a)
        if ''.join(a).startswith('直播'):
            NET_TOTAL = ["net.if.out.bits/iface=bond0", "net.if.in.bits/iface=bond0"]
            # endpoint="sr006.ct-zjhz-04.c4hcdn.cn"
            graph_data = []
            try:
                flow_counters = NET_TOTAL
                endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
                # graph_data 从query 取出的单个endpoint的信息（包含数据）
                query_result = rrdgraph.graph_query(endpoint_counters)
                # print len(query_result)
                for i in range(0, len(query_result)):
                    x = query_result[i]
                    # print x
                    try:
                        xv = [[float(v["timestamp"] * 1000), (v["value"])] for v in x["Values"]]
                        data_dict = {
                            "data": xv,
                            "name": "设备负载",
                            "cf": 'AVERAGE',
                            "endpoint": endpoint,
                            "counter": query_result[i]['counter'],
                        }
                        graph_data.append(data_dict)
                        # print graph_data
                    except:
                        pass
                GD = json.dumps(graph_data)
            except:
                pass
        else:
            NET_TOTAL = ["net.if.out.bits/iface=eth0","net.if.in.bits/iface=eth0"]
            # endpoint="sr006.ct-zjhz-04.c4hcdn.cn"
            graph_data = []
            try:
                flow_counters = NET_TOTAL
                endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
                # graph_data 从query 取出的单个endpoint的信息（包含数据）
                query_result = rrdgraph.graph_query(endpoint_counters)
                # print len(query_result)
                for i in range(0, len(query_result)):
                    x = query_result[i]
                    # print x
                    try:
                        xv = [[float(v["timestamp"] * 1000), (v["value"])] for v in x["Values"]]
                        data_dict = {
                            "data": xv,
                            "name": "设备负载",
                            "cf": 'AVERAGE',
                            "endpoint": endpoint,
                            "counter": query_result[i]['counter'],
                        }
                        graph_data.append(data_dict)
                        # print graph_data
                    except:
                        pass
                GD = json.dumps(graph_data)
            except:
                pass

    return render(request,'view/alarm/chart_server_networkbit.html',locals())


def Chart_Server_network_error(request,endpoint):
    """故障设备网卡error变化"""
    if request.method == 'GET':
        """设备服务端口及状态"""
        openfalcon_sql = """
                        select c.grp_name from `host` a,grp_host b ,grp c  where a.id=b.host_id 
                        and b.grp_id=c.id and a.hostname='%s';""" % (endpoint)
        openfalcon = db_falcon.mysql_command(openfalcon_sql)
        a = [grp_name[0] for grp_name in openfalcon]
        # print ''.join(a)
        if ''.join(a).startswith('直播'):
            NET_TOTAL = ["net.if.out.dropped/iface=bond0","net.if.in.dropped/iface=bond0","net.if.out.errors/iface=bond0","net.if.in.errors/iface=bond0"]
            # endpoint="sr006.ct-zjhz-04.c4hcdn.cn"
            graph_data = []
            try:
                flow_counters = NET_TOTAL
                endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
                # graph_data 从query 取出的单个endpoint的信息（包含数据）
                query_result = rrdgraph.graph_query(endpoint_counters)
                # print len(query_result)
                for i in range(0, len(query_result)):
                    x = query_result[i]
                    # print x
                    try:
                        xv = [[float(v["timestamp"] * 1000), (v["value"])] for v in x["Values"]]
                        data_dict = {
                            "data": xv,
                            "name": "设备负载",
                            "cf": 'AVERAGE',
                            "endpoint": endpoint,
                            "counter": query_result[i]['counter'],
                        }
                        graph_data.append(data_dict)
                        #print graph_data
                    except:
                        pass
                GD = json.dumps(graph_data)
            except:
                pass
        else:
            NET_TOTAL = ["net.if.out.dropped/iface=eth0", "net.if.in.dropped/iface=eth0",
                         "net.if.out.errors/iface=eth0", "net.if.in.errors/iface=eth0"]
            # endpoint="sr006.ct-zjhz-04.c4hcdn.cn"
            graph_data = []
            try:
                flow_counters = NET_TOTAL
                endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
                # graph_data 从query 取出的单个endpoint的信息（包含数据）
                query_result = rrdgraph.graph_query(endpoint_counters)
                # print len(query_result)
                for i in range(0, len(query_result)):
                    x = query_result[i]
                    # print x
                    try:
                        xv = [[float(v["timestamp"] * 1000), (v["value"])] for v in x["Values"]]
                        data_dict = {
                            "data": xv,
                            "name": "设备负载",
                            "cf": 'AVERAGE',
                            "endpoint": endpoint,
                            "counter": query_result[i]['counter'],
                        }
                        graph_data.append(data_dict)
                        #print graph_data
                    except:
                        pass
                GD = json.dumps(graph_data)
            except:
                pass

    return render(request,'view/alarm/chart_server_networkerror.html',locals())


def Chart_Server_http(request,endpoint):
    """故障设备http服务请求数"""
    if request.method == 'GET':
        NET_TOTAL = ["ss.estab","ss.timewait"]
        # endpoint="sr006.ct-zjhz-04.c4hcdn.cn"
        graph_data = []
        try:
            flow_counters = NET_TOTAL
            endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
            # graph_data 从query 取出的单个endpoint的信息（包含数据）
            query_result = rrdgraph.graph_query(endpoint_counters)
            # print len(query_result)
            for i in range(0, len(query_result)):
                x = query_result[i]
                # print x
                try:
                    xv = [[float(v["timestamp"] * 1000), (v["value"])] for v in x["Values"]]
                    data_dict = {
                        "data": xv,
                        "name": "设备负载",
                        "cf": 'AVERAGE',
                        "endpoint": endpoint,
                        "counter": query_result[i]['counter'],
                    }
                    graph_data.append(data_dict)
                    # print graph_data
                except:
                    pass
            GD = json.dumps(graph_data)
        except:
            pass

    return render(request,'view/alarm/chart_server_httpservices.html',locals())
