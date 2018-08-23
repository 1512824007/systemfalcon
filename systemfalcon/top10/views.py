# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from top10.models import end_va_cou, cluster_nic, date_graph
from openfalcon.models import Roomname
from qs_host import sf
from topology import all_c
from django.db.models import Sum
import MySQLdb
import time
import os
import json
from collections import Counter
from HcGraph import chart_room_network
import mysql_graph, mysql_falcon
from top10.scrpits import rrdgraph
import random
db_falcon = mysql_falcon.db_operate()
db_graph = mysql_graph.db_operate()

# Create your views here.
@login_required
def index(request):

    start_cpu = end_va_cou.objects.filter(counter='cpu_use').values_list('add_date').order_by('-add_date')[:1]
    start_mem = end_va_cou.objects.filter(counter='mem.memused.percent').values_list('add_date').order_by('-add_date')[:1]
    start_disk = end_va_cou.objects.filter(
        counter__contains='df.statistics.used.percent').values_list('add_date').order_by('-add_date')[:1]
    start_load = end_va_cou.objects.filter(counter='load.1min').values_list('add_date').order_by('-add_date')[:1]
    start_d = cluster_nic.objects.filter(counter__contains='net.if').values_list('add_date').order_by('-add_date')[:1]
    start_nic = start_d[0][0]
    sort_by = '-value'
    top = 10
    s_cpu = end_va_cou.objects.filter(counter='cpu_use').filter(value__lt=101).filter(add_date=start_cpu).order_by(sort_by)[:top]
    s_mem = end_va_cou.objects.filter(counter='mem.memused.percent').filter(add_date=start_mem).order_by(sort_by)[:top]
    s_disk = end_va_cou.objects.filter(
        counter__contains='df.statistics.used.percent').filter(add_date=start_disk).order_by(sort_by)[:top]
    s_load = end_va_cou.objects.filter(counter='load.1min').filter(add_date=start_load).order_by(sort_by)[:top]

    sql_net = "select top10_cluster_nic.endpoint , \
    sum(top10_cluster_nic.speed) as total_speed, \
    sum(top10_cluster_nic.value/1024/1024) as total_value, \
    cast((sum(top10_cluster_nic.value/1024/1024)/sum(top10_cluster_nic.speed)*100) as decimal(9,2)) as c \
    from top10_cluster_nic where top10_cluster_nic.counter like '%%net.if%%' \
    and top10_cluster_nic.add_date = %s \
    and top10_cluster_nic.speed != 0 \
    group by top10_cluster_nic.endpoint order by c desc limit 10" % start_nic

    conn = MySQLdb.connect('127.0.0.1', 'root', '123321', 'my_web')
    cur = conn.cursor()
    cur.execute(sql_net)
    s_net = cur.fetchall()
    conn.close()

    return render(request, 'top10/index_top10.html', {"cpu": s_cpu, "mem": s_mem, "net": s_net,
                                                   "disk": s_disk,"load": s_load})

@login_required
def ss_ss(request, roomname, pro, begin, over):
    s = all_c()
    counter = 'ss.estab'
    s.room_pro_t(counter, roomname, pro, int(begin), int(over))

    start_d = date_graph.objects.values_list('add_date').order_by('-add_date')[:1]
    start = start_d[0][0]

    s = str(list(Roomname.objects.filter(name=roomname).values_list('abbr_name')))
    import re
    p = re.split('[\']', s)[1]
    s_ss = date_graph.objects.filter(endpoint__icontains=p).filter(project=pro).filter(add_date=start).all()
    f1 = '/systemfalcon/systemfalcon/static/top10/{0}/{1}/{2}/room_service'.format(counter, roomname, pro)
    f2 = '/systemfalcon/systemfalcon/static/top10/{0}/{1}/{2}/room_service_max_min'.format(counter, roomname, pro)
    with open(f2, 'r') as f:
        m = f.readline()
    if m == '':
        max = ''
        min = ''
    else:
        max = m.split()[0]
        min = m.split()[1]

    with open(f1,'r') as f:
        graph_data = f.readline()
    return render(request, 'top10/UserRequest_idc.html', {"s_ss": s_ss, "graph_data": graph_data,
                                                         'max_data': max, 'min_data': min,
                                                         'idc_name': roomname})


@login_required
def Device_graph(request, hostname, start, over):
    s = int(start)
    o = int(over)
    counter1 = ['ss.estab',
                'df.statistics.used.percent',
                'mem.memused.percent',
                'cpu.idle',
                'load.1min',
                'net.if.out.bits']
    e_c = []
    for i in counter1:
        e_c.append(sf(hostname, i, s, o))
    ec = json.dumps(list(eval(str(e_c).replace("u\'","\'").replace("(","").replace(")","").replace(",,",","))))
    return render(request, 'top10/Device_graph.html', {"host": hostname, "ec": ec})


@login_required
def idc_top10(request):
    start_d = cluster_nic.objects.filter(counter__contains='net.if').values_list('add_date').order_by('-add_date')[:1]
    start_nic = start_d[0][0]
    sql_nic = "select top10_cluster_nic.idc , \
        sum(top10_cluster_nic.speed) as total_speed, \
        round(sum(top10_cluster_nic.value/1024/1024),0) as total_value, \
        cast((sum(top10_cluster_nic.value/1024/1024)/sum(top10_cluster_nic.speed)*100) as decimal(9,2)) as c \
        from top10_cluster_nic where top10_cluster_nic.counter like '%%net.if%%' \
        and top10_cluster_nic.add_date = %s \
        and top10_cluster_nic.speed != 0 \
        group by top10_cluster_nic.idc order by c desc limit 10" % start_nic

    conn = MySQLdb.connect('127.0.0.1', 'root', '123321', 'my_web')
    cur = conn.cursor()
    cur.execute(sql_nic)
    #s_nic = cur.fetchall()
    s_nic = (('nic_idc_name', 2000.0, 1500, 80),)

    conn.close()
    room_all = list(Roomname.objects.values('abbr_name', 'name'))
    random.shuffle(room_all)
    room_all =  room_all[:10]
    return render(request, 'top10/idc_top10.html', {"nic": s_nic, "room_all": room_all})


@login_required
def idc_network_graph(request,roomname):
    chart_room_network.Chart_Network_Live(roomname)
    chart_room_network.Chart_Network_Media(roomname)
    chart_room_network.Chart_Network_Web(roomname)
    return render(request, 'top10/idc_network_graph.html', {'roomname': json.dumps(roomname)})


@login_required
def icmp_graph(request, s_d):
    shost = s_d.split(">", 1)[0]
    dhost = s_d.split(">", 1)[1]
    return render(request, 'top10/icmp_graph.html', locals())

@login_required
def icmp_detail(request, s_d):
    try:
        shost = s_d.split("&gt;", 1)[0]
        dhost = s_d.split("&gt;", 1)[1]
    except:
        shost = s_d.split(">", 1)[0]
        dhost = s_d.split(">", 1)[1]
    sql_idc = "select name,abbr_name from idc_idc ;"
    idc = [['name','abbr_name']]

    for i in idc:
        if i[0] in shost:
            s_abbr_name = i[1].lower()
        if i[0] in dhost:
            d_abbr_name = i[1].lower()
            if d_abbr_name == 'ct-zjhz-04':
                d_abbr_name = 'ct-zjhz-02'
    sql = "select distinct endpoint from endpoint,endpoint_counter where counter like 'live.icmp%' \
          and endpoint.id=endpoint_counter.endpoint_id;"
    cou = db_graph.mysql_command(sql)

    sql2 = "select distinct counter from endpoint,endpoint_counter where counter like 'live.icmp.%' \
            or counter like 'live.linkspeed%'\
            and endpoint.id=endpoint_counter.endpoint_id;"
    cou2 = db_graph.mysql_command(sql2)
    e_c = []
    endpoint = ''
    for i in cou:
        if s_abbr_name in i[0]:
            endpoint = i[0]
    flow_counters = []
    flow_counters_2 = []
    flow_counters_3 = []
    flow_counters_4 = []
    for i in cou2:
        endpoint_index = i[0].split("/", 1)[1].split("=", 1)[0]
        if endpoint:
            if d_abbr_name in endpoint_index:
                counter = i[0]
                if 'avg' in counter or 'max' in counter or 'min' in counter:
                    flow_counters.append(counter)
                elif 'loss' in counter:
                    flow_counters_2.append(counter)
                elif 'mdev' in counter:
                    flow_counters_3.append(counter)
                else:
                    flow_counters_4.append(counter)
    GD = json.dumps([])
    GD_2 = json.dumps([])
    GD_3 = json.dumps([])
    GD_4 = json.dumps([])
    try:
        graph_data = []
        endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters]
        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        try:
            start0 = request.GET['start']
            end0 = request.GET['end']
            query_result = rrdgraph.graph_query(endpoint_counters,start=int(start0),end=int(end0))
        except:
            query_result = rrdgraph.graph_query(endpoint_counters,start=int(time.time())-3600,end=int(time.time()))
        for i in range(0, len(query_result)):
            x = query_result[i]
            # print x
            try:
                xv = []
                if x["Values"] != None:
                    for v in x['Values']:
                        if v["value"] == None:
                            s = [v["timestamp"] * 1000.0, 0]
                        else:
                            s = [v["timestamp"] * 1000.0, v["value"]]
                        xv.append(s)
                data_dict = {
                    "data": xv,
                    "name": "设备负载",
                    "cf": 'AVERAGE',
                    "endpoint": endpoint,
                    "counter": query_result[i]['counter'],
                }
                graph_data.append(data_dict)
            except:
                pass
        GD = json.dumps(graph_data)


        graph_data = []
        endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters_2]
        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        try:
            start0 = request.GET['start']
            end0 = request.GET['end']
            query_result = rrdgraph.graph_query(endpoint_counters, start=int(start0), end=int(end0))
        except:
            query_result = rrdgraph.graph_query(endpoint_counters, start=int(time.time()) - 3600, end=int(time.time()))
        for i in range(0, len(query_result)):
            x = query_result[i]
            # print x
            try:
                xv = []
                if x["Values"] != None:
                    for v in x['Values']:
                        if v["value"] == None:
                            s = [v["timestamp"] * 1000.0, 0]
                        else:
                            s = [v["timestamp"] * 1000.0, v["value"]]
                        xv.append(s)
                data_dict = {
                    "data": xv,
                    "name": "设备负载",
                    "cf": 'AVERAGE',
                    "endpoint": endpoint,
                    "counter": query_result[i]['counter'],
                }
                graph_data.append(data_dict)
            except:
                pass
        GD_2 = json.dumps(graph_data)

        graph_data = []
        endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters_3]
        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        try:
            start0 = request.GET['start']
            end0 = request.GET['end']
            query_result = rrdgraph.graph_query(endpoint_counters, start=int(start0), end=int(end0))
        except:
            query_result = rrdgraph.graph_query(endpoint_counters, start=int(time.time()) - 3600, end=int(time.time()))
        for i in range(0, len(query_result)):
            x = query_result[i]
            # print x
            try:
                xv = []
                if x["Values"] != None:
                    for v in x['Values']:
                        if v["value"] == None:
                            s = [v["timestamp"] * 1000.0, 0]
                        else:
                            s = [v["timestamp"] * 1000.0, v["value"]]
                        xv.append(s)
                data_dict = {
                    "data": xv,
                    "name": "设备负载",
                    "cf": 'AVERAGE',
                    "endpoint": endpoint,
                    "counter": query_result[i]['counter'],
                }
                graph_data.append(data_dict)
            except:
                pass
        GD_3 = json.dumps(graph_data)

        graph_data = []
        endpoint_counters = [{'endpoint': endpoint, 'counter': i} for i in flow_counters_4]
        # graph_data 从query 取出的单个endpoint的信息（包含数据）
        try:
            start0 = request.GET['start']
            end0 = request.GET['end']
            query_result = rrdgraph.graph_query(endpoint_counters, start=int(start0), end=int(end0))
        except:
            query_result = rrdgraph.graph_query(endpoint_counters, start=int(time.time()) - 3600, end=int(time.time()))
        for i in range(0, len(query_result)):
            x = query_result[i]
            # print x
            try:
                xv = []
                if x["Values"] != None:
                    for v in x['Values']:
                        if v["value"] == None:
                            s = [v["timestamp"] * 1000.0, 0]
                        else:
                            s = [v["timestamp"] * 1000.0, v["value"]]
                        xv.append(s)
                data_dict = {
                    "data": xv,
                    "name": "设备负载",
                    "cf": 'AVERAGE',
                    "endpoint": endpoint,
                    "counter": query_result[i]['counter'],
                }
                graph_data.append(data_dict)
            except:
                pass
        GD_4 = json.dumps(graph_data)
    except Exception as e:
        pass
    return render(request, 'top10/icmp_detail.html', locals())


@login_required
def ec(request, s_d):
    shost = s_d.split(">", 1)[0]
    dhost = s_d.split(">", 1)[1]
    return render(request, 'top10/icmp_graph.html', locals())

@login_required
def Bandwidth(request):
    return render(request,'top10/Bandwidth.html')
    start_d = cluster_nic.objects.filter(counter__contains='net.if').values_list('add_date').order_by('-add_date')[:1]
    start_nic = start_d[0][0]

    sql_liv = 'select a.hostname  from host as a,grp_host as t where t.host_id = a.id and t.grp_id = 5;'
    live_host = db_falcon.mysql_command(sql_liv)
    t = [str(i[0]) for i in live_host]
    live = tuple(t)
    live_sql = "select d.idc , \
            sum(d.speed) as total_speed, \
            round(sum(d.value/1024/1024),0) as total_value, \
            cast((sum(d.value/1024/1024)/sum(d.speed)*100) as decimal(9,2)) as c \
            from system_openfalcon.top10_cluster_nic as d \
            where  d.endpoint in %s \
            and d.counter like '%%net.if%%' \
            and d.add_date = %s \
            and d.speed != 0 \
            group by d.idc order by c desc limit 10" % (live,start_nic)

    sql_web = 'select a.hostname  from host as a,grp_host as t where t.host_id = a.id and t.grp_id = 44;'
    web_host = db_falcon.mysql_command(sql_web)
    t1 = [str(i[0]) for i in web_host]
    web = tuple(t1)
    web_sql = "select d.idc , \
                sum(d.speed) as total_speed, \
                round(sum(d.value/1024/1024),0) as total_value, \
                cast((sum(d.value/1024/1024)/sum(d.speed)*100) as decimal(9,2)) as c \
                from system_openfalcon.top10_cluster_nic as d \
                where  d.endpoint in %s \
                and d.counter like '%%net.if%%' \
                and d.add_date = %s \
                and d.speed != 0 \
                group by d.idc order by c desc limit 10" % (web, start_nic)


    conn = MySQLdb.connect('127.0.0.1', 'root', '123321', 'my_web')
    cur = conn.cursor()

    cur.execute(live_sql)
    live_nic = cur.fetchall()

    cur.execute(web_sql)
    web_nic = cur.fetchall()

    conn.close()

    room_all = Roomname.objects.values('abbr_name', 'name')
    sql_grp = 'select grp_name  from grp'
    grp = db_falcon.mysql_command(sql_grp)

    return render(request, 'top10/Bandwidth.html', locals())


@login_required
def band(request):
    try:
        start = int(request.GET['start'])
        end = int(request.GET['end'])
        grp = request.GET['grp']
        roomname = request.GET['roomname']
        counter = 'net.out.bits'

        group = json.dumps([grp])
        cou = json.dumps([counter])
        room = json.dumps([roomname])
        host0 =  "select host.hostname from grp,host,grp_host where grp.grp_name = '%s' \
        and host.id = grp_host.host_id and grp.id =grp_host.grp_id ;" %(grp)
        grp_host_l = db_falcon.mysql_command(host0)
        grp_host_t = tuple([str(i[0]) for i in grp_host_l])

        host1 = "select a.hostname from device_server as a,idc_idc as b where a.idc_id = b.id \
        and b.name = '%s' and a.hostname in %s" %(roomname,grp_host_t)
        hostnames = [['a.hostname']]
        a = {}
        dict_count = Counter(a)

        for endpoint in hostnames:

            sql_nic = "select hostname,nic from device_server where hostname = '{0}';".format(endpoint[0])
            NET_OUT_Other = ["net.if.out.bits/iface={0}".format('ens33')]
            try:
                query_result = rrdgraph.graph_query(endpoint,NET_OUT_Other,start=start,end=end)
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

        data = list(sorted(dict_count.items()))
        GD = json.dumps(data)

        dir1 = '/systemfalcon/systemfalcon/static/top10/{0}/{1}/{2}/'.format(counter, roomname, grp)
        f1 = '/systemfalcon/systemfalcon/static/top10/{0}/{1}/{2}/room_band'.format(counter, roomname, grp)
        f2 = '/systemfalcon/systemfalcon/static/top10/{0}/{1}/{2}/room_band_max_min'.format(counter, roomname, grp)
        
        if not os.path.exists(f1):
            if not os.path.exists(dir1):
                os.makedirs(dir1)
            os.system('touch ' + f1)
            os.system('touch ' + f2)
        with open(f1, 'w') as f:
            f.write(GD)
        try:
            max_data = max(dict_count.values())
            min_data = min(dict_count.values())

            with open(f2, 'w') as a:
                a.write(str(max_data) + ' ' + str(min_data))
        except Exception as e:
            pass

    except Exception as e:
        group = json.dumps([])
        cou = json.dumps([])
        room = json.dumps([])

    return render(request, 'top10/band_idc.html', locals())


@login_required
def project_hostlist(request,pro):

    sql_host = "select ds.hostname,bp.name,idc.name \
    from device_server as ds,business_clusterserver as bcs,business_cluster as bc,business_project as bp,idc_idc as idc \
    where  bp.id=bc.project_id \
    and bc.id=bcs.cluster_id \
    and ds.id=bcs.device_id \
    and ds.idc_id = idc.id \
    and bp.name = '%s' order by idc.name" %(pro)
    all_pro = [['ds.hostname','bp.name','idc.name']]

    paginator = Paginator(all_pro, 12)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'top10/project_hostlist.html', locals())
