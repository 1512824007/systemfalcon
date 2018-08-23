# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from openfalcon.models import Roominfo,Aralminfo,Roomname,Alarm_op
from django.db.models import Q
import mysql,mysql_falcon,mysql_oms,mysql_systemfalcon
from django.core.paginator import Paginator,InvalidPage,EmptyPage
import json
import sys
import os,time
import subprocess
from top10.models import end_va_cou,cluster_nic, date_graph
from top10.topology import m_angle_band
from django.db.models import Sum
import MySQLdb
from  HcGraph import chart_room,chart_room_network,chart_room_service,chart_device_port
from userauth.in_module import in_module, return_device_group


# Create your views here.

reload(sys)
sys.setdefaultencoding('utf-8')
sys.getdefaultencoding()

db = mysql.db_operate()
db_falcon = mysql_falcon.db_operate()
db_oms = mysql_oms.db_operate()
db_systemfalcon = mysql_systemfalcon.db_operate()


class Falcon_index():
    """首页"""


@login_required
def Map(request):
    return render(request,'view/Map.html',locals())

@login_required
def index(request):
    '''Dashboard'''
    Alarm_info = Roominfo.objects.all()

    dashboard_event = "true" if in_module(request,'Dashboard_event') else "false"
    Dm = "true" if in_module(request, 'Dashboard_map') else "false"

    cluster = return_device_group(request,)
    device_event = Roominfo.objects.filter(cluster__in=cluster).filter(metric__in=['agent.alive', 'net.port.listen', 'proc.num', 'df.bytes.free.percent'])

    app_event = Roominfo.objects.filter(cluster__in=cluster).exclude(metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped',
                    'net.if.in.errors',
                    'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                    'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                    'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                    'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                    'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                    'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                    'net.if.total.packets'])
    network_event = Roominfo.objects.filter(cluster__in=cluster).filter(metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                    'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                    'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                    'net.if.total.bytes',
                    'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                    'net.if.out.dropped',
                    'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                    'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                    'net.if.total.packets'])
    return render(request, 'view/Dashboard.html', locals())


@login_required
def event(request):
    '''监控首页'''

    event = Roominfo.objects.all().order_by('hostname')
    room_all = Roomname.objects.values('abbr_name', 'name')
    sql_host = "select hostname from device_server where cpu != '[]' and hostname != 'NULL'"
    sql_pro = "select name from business_project"
    pro = db_oms.mysql_command(sql_pro)
    host = db_oms.mysql_command(sql_host)

    return render(request, 'view/MonitorInfo.html', locals())

@login_required
def TroubleList(request):
    '''故障列表'''
    ps = dict()
    alarm_group = Aralminfo.objects.filter(alarm_status='告警').filter(alarm_status_ok='').values('room').distinct().order_by('room')
    cluster_group = Aralminfo.objects.filter(alarm_status='告警').filter(alarm_status_ok='').values('cluster').distinct().order_by('cluster')
    alarmlist = Aralminfo.objects.filter(alarm_status='告警').filter(alarm_status_ok='').values('metric').distinct().order_by('metric')
    if 'room' in request.GET and 'product' not in request.GET:
        room_select = ps["room"] = request.GET['room']
        qset = (
            Q(room=room_select) &
            Q(alarm_status='告警') &
            Q(alarm_status_ok='')
        )
        """设备告警查询"""
        device_event = Aralminfo.objects.filter(
            metric__in=['agent.alive', 'net.port.listen', 'proc.num', 'df.bytes.free.percent']).filter(qset).order_by(
            '-start_date')
        app_event = Aralminfo.objects.exclude(
            metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped',
                        'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions',
                        'net.if.out.compressed',
                        'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).order_by('-start_date')
        network_event = Aralminfo.objects.filter(
            metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes',
                        'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).order_by('-start_date')
        """统计各类产品总数"""
        device_count = Aralminfo.objects.filter(
            metric__in=['agent.alive', 'net.port.listen', 'proc.num', 'df.bytes.free.percent']).filter(qset).count()
        app_count = Aralminfo.objects.exclude(
            metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped',
                        'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions',
                        'net.if.out.compressed',
                        'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).count()
        network_count = Aralminfo.objects.filter(
            metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes',
                        'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).count()

        # alarm_list = Aralminfo.objects.filter(qset).order_by('-start_date')
        counts = Aralminfo.objects.filter(qset).count()
        # paginator = Paginator(device_event, 10)
        # try:
        #     page = int(request.GET.get('page', '1'))
        # except ValueError:
        #     page = 1
        #
        # try:
        #     info = paginator.page(page)
        # except:
        #     info = paginator.page(paginator.mun_pages)
        return render(request, 'view/TroubleList.html',
                      {"device_event": device_event, 'counts': counts,
                       'ps': ps, 'alarm_group': alarm_group, 'cluster_group': cluster_group, 'app_event': app_event,
                       'network_event': network_event,'alarm_list':alarmlist,
                       'device_count': device_count, 'app_count': app_count, 'network_count': network_count})
    elif 'product' in request.GET and 'room' in request.GET and  'alarm' not in request.GET:
        room_select = ps["room"] = request.GET['room']
        prodoct_select = ps["product"] = request.GET['product']
        qset = (
            Q(room=room_select)&
            Q(cluster=prodoct_select)&
            Q(alarm_status='告警') &
            Q(alarm_status_ok='')
        )
        """设备告警查询"""
        device_event = Aralminfo.objects.filter(
            metric__in=['agent.alive', 'net.port.listen', 'proc.num', 'df.bytes.free.percent']).filter(qset).order_by(
            '-start_date')
        app_event = Aralminfo.objects.exclude(
            metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped',
                        'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions',
                        'net.if.out.compressed',
                        'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).order_by('-start_date')
        network_event = Aralminfo.objects.filter(
            metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes',
                        'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).order_by('-start_date')
        """统计各类产品总数"""
        device_count = Aralminfo.objects.filter(
            metric__in=['agent.alive', 'net.port.listen', 'proc.num', 'df.bytes.free.percent']).filter(qset).count()
        app_count = Aralminfo.objects.exclude(
            metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped',
                        'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions',
                        'net.if.out.compressed',
                        'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).count()
        network_count = Aralminfo.objects.filter(
            metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes',
                        'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).count()

        # alarm_list = Aralminfo.objects.filter(qset).order_by('-start_date')
        counts = Aralminfo.objects.filter(qset).count()

        return render(request, 'view/TroubleList.html',
                      {"device_event": device_event, 'counts': counts,
                       'ps': ps, 'alarm_group': alarm_group, 'cluster_group': cluster_group, 'app_event': app_event,
                       'network_event': network_event,'alarm_list':alarmlist,
                       'device_count': device_count, 'app_count': app_count, 'network_count': network_count})
    elif 'product' in request.GET and 'room' in request.GET and 'alarm' in request.GET:
        room_select = ps["room"] = request.GET['room']
        prodoct_select = ps["product"] = request.GET['product']
        alarm_select = ps["alarm"] = request.GET['alarm']
        qset = (
            Q(room=room_select)&
            Q(cluster=prodoct_select)&
            Q(metric=alarm_select)&
            Q(alarm_status='告警') &
            Q(alarm_status_ok='')
        )
        """设备告警查询"""
        device_event = Aralminfo.objects.filter(
            metric__in=['agent.alive', 'net.port.listen', 'proc.num', 'df.bytes.free.percent']).filter(qset).order_by(
            '-start_date')
        app_event = Aralminfo.objects.exclude(
            metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped',
                        'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions',
                        'net.if.out.compressed',
                        'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).order_by('-start_date')
        network_event = Aralminfo.objects.filter(
            metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes',
                        'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).order_by('-start_date')
        """统计各类产品总数"""
        device_count = Aralminfo.objects.filter(
            metric__in=['agent.alive', 'net.port.listen', 'proc.num', 'df.bytes.free.percent']).filter(qset).count()
        app_count = Aralminfo.objects.exclude(
            metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped',
                        'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions',
                        'net.if.out.compressed',
                        'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).count()
        network_count = Aralminfo.objects.filter(
            metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes',
                        'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).count()

        # alarm_list = Aralminfo.objects.filter(qset).order_by('-start_date')
        counts = Aralminfo.objects.filter(qset).count()

        return render(request, 'view/TroubleList.html',
                      {"device_event": device_event, 'counts': counts,
                       'ps': ps, 'alarm_group': alarm_group, 'cluster_group': cluster_group, 'app_event': app_event,
                       'network_event': network_event,'alarm_list':alarmlist,
                       'device_count':device_count,'app_count':app_count,'network_count':network_count})
    else:
        qset = (
            Q(alarm_status='告警') &
            Q(alarm_status_ok='')
        )
        """设备告警查询"""
        device_event = Aralminfo.objects.filter(metric__in=['agent.alive','net.port.listen','proc.num','df.bytes.free.percent']).filter(qset).order_by('-start_date')
        app_event = Aralminfo.objects.exclude(
            metric__in=[ 'agent.alive','net.port.listen','net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes','net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped','proc.num','df.bytes.free.percent',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).order_by('-start_date')
        network_event = Aralminfo.objects.filter(
            metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes',
                        'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).order_by('-start_date')
        """统计各类产品总数"""
        device_count = Aralminfo.objects.filter(metric__in=['agent.alive','net.port.listen','proc.num','df.bytes.free.percent']).filter(qset).count()
        app_count = Aralminfo.objects.exclude(
            metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped',
                        'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions',
                        'net.if.out.compressed',
                        'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).count()
        network_count = Aralminfo.objects.filter(
            metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes',
                        'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets']).filter(qset).count()



        # alarm_list = Aralminfo.objects.filter(qset).order_by('-start_date')
        counts = Aralminfo.objects.filter(qset).count()
        # paginator = Paginator(device_event, 10)
        # try:
        #     page = int(request.GET.get('page', '1'))
        # except ValueError:
        #     page = 1
        #
        # try:
        #     info = paginator.page(page)
        # except:
        #     info = paginator.page(paginator.mun_pages)
        return render(request, 'view/TroubleList.html',
                      {"device_event": device_event,'counts': counts,
                       'ps': ps,'alarm_group':alarm_group,'cluster_group':cluster_group,
                       'app_event':app_event,'network_event':network_event,
                       'alarm_list':alarmlist,'device_count':device_count,'app_count':app_count,'network_count':network_count})

    # return render(request, 'view/TroubleList.html',locals())


@login_required
def TroubleBI(request):
    '''故障统计'''
    if 'start_time' in request.GET and 'end_time' in request.GET and request.GET['start_time'] not in '' and request.GET['end_time'] not in '':
        print 'Select time is data!!'
        start_time = request.GET['start_time']
        end_time = request.GET['end_time']
        """机房占比"""
        sql = "select room,count(counts) from openfalcon_aralminfo where start_date between'%s' and '%s' group by room;" %(start_time,end_time)
        query_result = db_systemfalcon.mysql_command(sql)
        graph_data = []
        if len(query_result):
            for i in range(0, len(query_result)):
                x = query_result[i]
                data_dict = {
                    'name': x[0],
                    'num': x[1],
                    'y': x[1],
                }
                graph_data.append(data_dict)

            GD = json.dumps(graph_data)
        else:
            print 'no data'
            GD = []
            pass

        """设备占比"""
        hostname = "select hostname,count(counts) from openfalcon_aralminfo where start_date between'%s' and '%s' group by hostname;" % (
        start_time, end_time)
        hostname_result = db_systemfalcon.mysql_command(hostname)
        hostname_data=[]
        if len(hostname_result):
            for i in range(0, len(hostname_result)):
                x = hostname_result[i]
                hostnames_dict = {
                    'name': x[0],
                    'num': x[1],
                    'y': x[1],
                }
                hostname_data.append(hostnames_dict)

            hostnames = json.dumps(hostname_data)
        else:
            print 'no data'
            hostnames = []
            pass

        """类型占比"""
        metric = "select metric,count(counts) from openfalcon_aralminfo where start_date between'%s' and '%s' group by metric;" % (
            start_time, end_time)
        metric_result = db_systemfalcon.mysql_command(metric)
        metric_data = []
        if len(metric_result):
            for i in range(0, len(metric_result)):
                x = metric_result[i]
                metrics_dict = {
                    'name': x[0],
                    'num': x[1],
                    'y': x[1],
                }
                metric_data.append(metrics_dict)

            metrics = json.dumps(metric_data)
        else:
            print 'no data'
            metrics = []
            pass
    else:
        print '7 days data!!'
        sql = "select room,count(counts) from openfalcon_aralminfo where replace(start_date,'-','') >=CURDATE()-7 group by room;"
        query_result = db_systemfalcon.mysql_command(sql)
        graph_data = []
        if len(query_result):
            for i in range(0, len(query_result)):
                x = query_result[i]
                data_dict = {
                    'name': x[0],
                    'num': x[1],
                    'y': x[1],
                }
                graph_data.append(data_dict)

            GD = json.dumps(graph_data)
        else:
            print 'no data'
            GD = []
            pass

        """设备占比"""
        hostname = "select hostname,count(counts) from openfalcon_aralminfo where replace(start_date,'-','') >=CURDATE()-7 group by hostname;"
        hostname_result = db_systemfalcon.mysql_command(hostname)
        hostname_data = []
        if len(hostname_result):
            for i in range(0, len(hostname_result)):
                x = hostname_result[i]
                hostnames_dict = {
                    'name': x[0],
                    'num': x[1],
                    'y': x[1],
                }
                hostname_data.append(hostnames_dict)

            hostnames = json.dumps(hostname_data)
        else:
            print 'no data'
            hostnames = []
            pass

        """类型占比"""
        metric = "select metric,count(counts) from openfalcon_aralminfo where replace(start_date,'-','') >=CURDATE()-7 group by metric;"
        metric_result = db_systemfalcon.mysql_command(metric)
        metric_data = []
        if len(metric_result):
            for i in range(0, len(metric_result)):
                x = metric_result[i]
                metrics_dict = {
                    'name': x[0],
                    'num': x[1],
                    'y': x[1],
                }
                metric_data.append(metrics_dict)

            metrics = json.dumps(metric_data)
        else:
            print 'no data'
            metrics = []
            pass
    return render(request, 'view/TroubleBI.html',{'GD':GD,'hostnames':hostnames,'metrics':metrics})


@login_required
def TroubleInfo(request):
    '''故障详情'''

    if request.method=="GET":
        hostname = request.GET['hostname']
        aralm = request.GET['aralm']
        alarm_info = Aralminfo.objects.filter(hostname=hostname).filter(aralm=aralm).filter(alarm_status_ok='')
        alarm_info1 = Aralminfo.objects.filter(hostname=hostname).filter(aralm=aralm).order_by('-id')[:1]
        hostname = hostname

        # 操作日志记录
        alarm_host_id = alarm_info1.values('id')
        host_id = int(alarm_host_id[0]['id'])
        alarm_op = Alarm_op.objects.filter(alarm_host_id=host_id).filter(alarm_host=hostname).filter(alarm=aralm).order_by('-id')[:1]

        sql = "select c.name,d.name from device_server a ,business_clusterserver b,business_cluster c ,business_project d where a.id=b.device_id  and b.cluster_id =c.id and c.project_id=d.id and a.hostname='%s';" % (
        hostname)
        info = db_oms.select_table(sql)
        info = [result for result in info]
        if len(info) > 0:
            cluster = info[0]
            project = info[1]
        else:
            cluster = '离线'
            project = '离线'
            pass

        sql_device = "select a.manufacturer,a.product_name,a.sn,a.os,a.memory,a.memory_size from device_server a where a.hostname='%s';" % (
        hostname)

        info_device = db_oms.select_table(sql_device)
        info_device = [result for result in info_device]
        if len(info_device) > 0:
            manufacturer = info_device[0]
            product_name = info_device[1]
            sn = info_device[2]
            os = info_device[3]
            memory = info_device[4]
            memory_size = info_device[5] * 1024 * 1024
        else:
            cluster = '离线'
            project = '离线'
            pass

        """设备服务端口及状态"""
        openfalcon_sql = """
        select c.tags from `host` a,grp_host b ,strategy c,grp_tpl d where a.id=b.host_id and b.grp_id=d.grp_id
        and d.tpl_id=c.tpl_id and c.metric='net.port.listen' and a.hostname='%s';""" %(hostname)
        openfalcon = db_falcon.mysql_command(openfalcon_sql)
        graph_data = []
        for i in openfalcon:
            ports= i[0]

        try:
            result = chart_device_port.Chart_Room(hostname,i[0])
            results =  result.replace("[[", "").replace("]]", "")
            data = {
                'ports':ports,
                'values':results,
            }

            graph_data.append(data)

        except:
            pass
        # print (graph_data)
	"""查询实时告警信息"""
        alarm_sql = """select hostname,count(*) from openfalcon_roominfo group by hostname order by hostname;"""

        alarm = db_systemfalcon.mysql_command(alarm_sql)
        # print alarm
        host_name = [host_name[0] for host_name in alarm]

        """相同机架设备状态"""
        rack_sql = """
        SELECT 
        DISTINCT a.hostname,e.`name`,d.`name`
         from device_server a,idc_idcrack b,business_clusterserver c,business_cluster d,business_project e,idc_idc h where 
        a.rack_id = b.id AND a.id=c.device_id and c.cluster_id = d.id and d.project_id=e.id and a.idc_id=h.id 
        and b.`name` in(select b.`name` from device_server a,idc_idcrack b  where a.rack_id = b.id and a.hostname='%s')
        and b.`name` in(select b.`name` from device_server a,idc_idcrack b,idc_idc c  where a.rack_id = b.id and a.idc_id=c.id 
        and h.`name` in(select c.`name` from device_server a,idc_idcrack b,idc_idc c  where a.rack_id = b.id and a.idc_id=c.id and a.hostname='%s')) ORDER BY d.`name`;
        """%(hostname,hostname)
        racks = db_oms.mysql_command(rack_sql)

        """相同网段设备状态"""
        netline_sql = """
        SELECT DISTINCT a.hostname,e.`name`,d.`name`
         from device_server a,idc_idcrack b,business_clusterserver c,business_cluster d,business_project e,device_serverinterface f ,idc_idcnetwork g,idc_idc h where 
        a.rack_id = b.id AND a.id=c.device_id and c.cluster_id = d.id and d.project_id=e.id  and a.id=f.device_id and f.network_id = g.id and a.idc_id=h.id 
        and g.gateway in(select b.gateway from device_server c ,device_serverinterface a ,idc_idcnetwork b where a.network_id=b.id and c.id=a.device_id and b.gateway not LIKE '10.32.%%' and c.hostname='%s' )
        and b.`name` in(select b.`name` from device_server a,idc_idcrack b,idc_idc c  where a.rack_id = b.id and a.idc_id=c.id 
        and h.`name` in(select c.`name` from device_server a,idc_idcrack b,idc_idc c  where a.rack_id = b.id and a.idc_id=c.id and a.hostname='%s')) ORDER BY d.`name`;        
        """%(hostname,hostname)
        netlines = db_oms.mysql_command(netline_sql)

        """相同服务角色设备状态"""
        clusters_sql ="""
        SELECT DISTINCT a.hostname,e.`name`,d.`name`
         from device_server a,idc_idcrack b,business_clusterserver c,business_cluster d,business_project e,device_serverinterface f ,idc_idcnetwork g,idc_idc h where 
        a.rack_id = b.id AND a.id=c.device_id and c.cluster_id = d.id and d.project_id=e.id  and a.id=f.device_id and f.network_id = g.id and a.idc_id=h.id
        and d.`name` in(SELECT d.`name` from device_server a,business_clusterserver c,business_cluster d,business_project e where  a.id=c.device_id and c.cluster_id = d.id and d.project_id=e.id and a.hostname='%s') 
        and h.`name` in(select c.`name` from device_server a,idc_idcrack b,idc_idc c  where a.rack_id = b.id and a.idc_id=c.id and a.hostname='%s') ORDER BY d.`name`;        
        """%(hostname,hostname)
        clusters = db_oms.mysql_command(clusters_sql)
    else:
        pass
    return render(request, 'view/TroubleInfo.html',
                  {'alarm_info': alarm_info, 'cluster': cluster, 'project': project, 'manufacturer': manufacturer
                      , 'product_name': product_name, 'sn': sn, 'os': os, 'memory_size': memory_size,
                   'result': graph_data, 'hostname': hostname, 'racks': racks, 'netlines': netlines,
                   'clusters': clusters, 'host_name': host_name, 'alarm_op': alarm_op})


@login_required
def ServerRoom(request):
    '''机房运行状态'''
    return render(request, 'view/ServerRoom.html',locals())


@login_required
def UserRequest(request):
    '''产品并发用户数'''
    start = date_graph.objects.values_list('add_date').order_by('-add_date')[:1]

    ss_clms = date_graph.objects.filter(counter='ss.estab').filter(add_date=start).filter(
        project='clms').values('idc').annotate(
        total_ssvalue=Sum("value")).values('idc', 'total_ssvalue').order_by('-total_ssvalue')[:10]
    ss_VOD_GSVC = date_graph.objects.filter(counter='ss.estab').filter(add_date=start).filter(
        project='VOD_GSVC').values('idc').annotate(
        total_ssvalue=Sum("value")).values('idc', 'total_ssvalue').order_by('-total_ssvalue')[:10]
    ss_web = date_graph.objects.filter(counter='ss.estab').filter(add_date=start).filter(
        project='GSweb').values('idc').annotate(
        total_ssvalue=Sum("value")).values('idc', 'total_ssvalue').order_by('-total_ssvalue')[:10]
    room_all = Roomname.objects.values('abbr_name', 'name')

    ss_pro = date_graph.objects.values('project').distinct()
    return render(request, 'view/UserRequest.html', {"ss_clms": ss_clms, "ss_web": ss_web, "ss_vod": ss_VOD_GSVC, 'room_all': room_all, 'ss_pro': ss_pro})


@login_required
def MonitorManage(request):
    '''系统配置'''
    return render(request, 'view/MonitorManage.html',locals())


@login_required
def ServerRoom_Detail(request,roomname):
    '''详情机房运行状态'''
    s = m_angle_band()
    speed = s.room_speed(roomname)
    room_name = Roomname.objects.filter(name=''.join(roomname).encode('utf-8'))
    room_event = Roominfo.objects.filter(room=''.join(roomname).encode('utf-8'))[:1]
    every_event = Roominfo.objects.filter(room=''.join(roomname).encode('utf-8'))
    device_event = Roominfo.objects.filter(room=''.join(roomname).encode('utf-8')).filter(metric__in=['agent.alive', 'net.port.listen', 'proc.num', 'df.bytes.free.percent'])
    app_event = Roominfo.objects.filter(room=''.join(roomname).encode('utf-8')).exclude(metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped',
                        'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions',
                        'net.if.out.compressed',
                        'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets'])
    network_event = Roominfo.objects.filter(room=''.join(roomname).encode('utf-8')).filter(metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                        'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                        'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                        'net.if.total.bytes',
                        'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                        'net.if.out.dropped',
                        'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                        'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                        'net.if.total.packets'])

    list_info = [[str(info) for info in range(5)]]
    #print(list_info)
    #chart_room.Chart_Room(roomname)

    m = open('/systemfalcon/systemfalcon/static/alarm/{0}/room_max_min'.format(roomname), 'r').readline()
    if m == '':
        max_data = ''
        min_data = ''
    else:
        max_data = m.split()[0]
        min_data = m.split()[1]

    change =''
    network =''
    gateway =''
    for i in range(0,len(list_info)):
        # change= list_info[i]
        if list_info[i][4] not in change:
            change +=list_info[i][4]+' '
        network += list_info[i][1]+'/'+list_info[i][2] +" "
        gateway += list_info[i][3]+" "

    """各产品设备列表"""
    ret =[]
    ret1 =[]
    oms_room = [['roomname1','roomname2']]
    for hostname in oms_room:
        clusters = [1,2,3]
        if clusters[0]:
            """有业务线查询相关业务线及机柜信息"""
            info = """select  a.hostname,c.ip,f.`name`,e.`name`,b.`name`
            from device_server a ,idc_idcrack b,device_serverinterface c,business_clusterserver d,business_cluster e,business_project f,idc_idc g
            where  a.rack_id=b.id and a.id=d.device_id  and a.id=c.device_id
            and d.cluster_id = e.id and e.project_id=f.id and a.idc_id=g.id and c.ip not LIKE "10.32.%%"
            and a.hostname='%s';"""%(hostname)
            rack_info = [['hostname','ip','f.name','e.name','b.name']]
            for i in [rack_info]:
                ret+=i

        else:
            """无业务线查询机柜信息"""
            rack = """select a.hostname,c.ip,'无业务','无集群',b.`name` 
                               from device_server a, idc_idcrack b,device_serverinterface c
                               where a.rack_id = b.id and a.id=c.device_id and c.ip not LIKE "10.32.%%" 
                               and a.hostname = '%s';""" %(hostname)
            rack_info1 = [['a.hostname','c.ip','无业务','无集群','b.name']]
            for i in [rack_info1]:
                ret1+=i
            # print rack_info1
    data = ret
    data1 = ret1

    return render(request, 'view/ServerRoom.html',{'room_event':room_event,'roomname': roomname,'speed': speed,
                                                   'room_name':room_name,'change':change,
                                                   'network':network,'gateway':gateway,
                                                   'max_data': max_data,
                                                   'min_data': min_data,'device_event':device_event,
                                                   'network_event':network_event,'app_event':app_event,
                                                   'every_event':every_event,
                                                   'data':data,'data1':data1})


@login_required
def Device_Detail(request, hostname):
    #host = hostname
    host = 'slavesql2'

    sql_base1 = "select device_serverinterface.ip,device_server.hostname, \
    idc_idc.abbr_name as idc \
    from idc_idc,device_serverinterface,device_server \
    where device_server.id=device_serverinterface.device_id \
    and device_server.idc_id=idc_idc.id  \
    and device_server.hostname='%s';" % host

    sql_base2 = "select a.*,b.name,c.name,d.name from device_server as a, idc_idc as b,idc_idcrack as c,  \
    business_cluster as d,business_clusterserver as e \
    where  a.idc_id=b.id and a.rack_id=c.id and d.id=e.cluster_id and e.device_id =a.id \
    and hostname='%s';" % host

    dd1 = [['ip','hostname','abbr_name' ]]
    dd2 = [['a.*','b.name','c.name','d.name']]
    ip = []
    for i in dd1:
        ip.append(i[0])
    clu = []
    for i in dd2:
        #clu.append(i[26])
        clu.append(i[3])

    sql_hw = "select cpu,hd,hd_size,nic,memory,memory_size from device_server where hostname='%s';" % host
    hw = [['cpu','hd','hd_size','nic','memory','memory_size']]
    hw_cpu = hw[0][0]
    hw_hd = hw[0][1]
    hw_hd_size = hw[0][2]
    hw_nic = hw[0][3]
    hw_mem = 'hw_mem'
    hw_mem_size = hw[0][5]
    hw_mem_num = 2
    e = int(time.time())-60
    s = e - 36000    
    Alarm_info = Roominfo.objects.filter(hostname=hostname).all()
    device_event = Roominfo.objects.filter(hostname=hostname).filter(
        metric__in=['agent.alive', 'net.port.listen', 'proc.num', 'df.bytes.free.percent'])
    app_event = Roominfo.objects.filter(hostname=hostname).exclude(
        metric__in=['agent.alive', 'net.port.listen', 'net.if.in.bits', 'net.if.in.compressed',
                    'net.if.in.dropped',
                    'net.if.in.errors',
                    'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                    'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                    'net.if.total.bytes', 'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                    'net.if.out.dropped', 'proc.num', 'df.bytes.free.percent',
                    'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                    'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                    'net.if.total.packets'])
    network_event = Roominfo.objects.filter(hostname=hostname).filter(
        metric__in=['net.if.in.bits', 'net.if.in.compressed', 'net.if.in.dropped', 'net.if.in.errors',
                    'net.if.in.fifo.errs', 'net.if.in.frame.errs', 'net.if.in.multicast', 'net.if.in.packets',
                    'net.if.in.percent', 'net.if.out.bits', 'net.if.in.bytes', 'net.if.out.bytes',
                    'net.if.total.bytes',
                    'net.if.out.carrier.errs', 'net.if.out.collisions', 'net.if.out.compressed',
                    'net.if.out.dropped',
                    'net.if.out.errors', 'net.if.out.fifo.errs', 'net.if.out.packets', 'net.if.out.percent',
                    'net.if.speed.bits', 'net.if.total.bits', 'net.if.total.dropped', 'net.if.total.errors',
                    'net.if.total.packets'])
    return render(request, 'view/Device.html', {"host": host,"ip": ip,
                                                "server": dd2[0],
                                                "clu": clu,
                                                "hw_cpu": hw_cpu,
                                                "hw_hd": hw_hd,
                                                "hw_hd_size": hw_hd_size,
                                                "hw_mem": hw_mem,
                                                "hw_mem_size": hw_mem_size,
                                                "hw_mem_num": hw_mem_num,
                                                "hw_nic":hw_nic, "s": s, "e": e,
                                                'Alarm_info': Alarm_info,
                                                'device_event': device_event, 'app_event': app_event,
                                                'network_event': network_event})


@login_required
def TroubleInfo_Add(request):
    """故障设备操作日志记录"""
    if request.method=="POST":
        alarm_host_id = request.POST['host_id']
        alarm_host = request.POST['name']
        alarm = request.POST['alarm']
        alarm_operation = request.POST['alarm_operation']
        Alarm_op.objects.update_or_create(alarm_host_id=alarm_host_id,alarm_host=alarm_host,alarm=alarm,alarm_operation=alarm_operation)
        # return redirect('/monitor/MonitorInfo/TroubleInfo/?hostname=%s&aralm=%s')%(alarm_host,alarm)
        return HttpResponse('提交成功')
    else:
        return HttpResponse("操作日志")


@login_required
def falcon(request):
    sql='select id,name,name_1,abbr_name_1,project_id,grp_name_id from oms_openfalcon;'
    counts='select count(*) from oms_openfalcon;'
    count= db.select_table(counts)
    results= db.mysql_command(sql)

    paginator = Paginator(results, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        result = paginator.page(page)
    except:
        result = paginator.page(paginator.num_pages)
    return render(request,'falcon_oms.html',{'result':result,'page':page,'paginator':paginator,'count':count[0]})


@login_required
def falcon_detail(request,id):
    sql="select id,name,name_1,abbr_name_1,project_id,grp_name_id from oms_openfalcon where id='%d';" %(int(id))
    falcon_sql = "select id,grp_name from grp order by id ;"
    result= db.mysql_command(sql)
    result_falcon= db_falcon.mysql_command(falcon_sql)
    if request.method == 'POST':
        grp_name_id = request.POST['grp_name_id']
        sql_grp = "update oms_openfalcon set grp_name_id='%s' where id='%d'; " %(grp_name_id,int(id))
        db.mysql_command(sql_grp)
        return redirect('/monitor/falcon/')
    return render(request,'falcon_detail.html',{'result':result,'result_falcon':result_falcon})


@login_required
def falcon_alarm_info(request):
    ps = dict()
    if 'start_time' in request.GET and 'end_time' in request.GET and 'alarm_select' in request.GET:
        start_time = ps['start_time']= request.GET['start_time'].encode('utf-8')
        end_time = ps["end_time"] = request.GET['end_time'].encode('utf-8')
        alarm_select =  ps["alarm_select"] =  request.GET['alarm_select']
        if start_time  not in '' and end_time not in '' and "恢复" in alarm_select:
            alarm_status=u'恢复'
            qset =(
                Q(start_date__gte = start_time)&
                Q(end_date__lte = end_time)&
                Q(alarm_status_ok = alarm_select)
            )
            alarm_list = Aralminfo.objects.filter(qset).order_by('-end_date')
            counts = Aralminfo.objects.filter(qset).count()
            all_counts = Aralminfo.objects.all().count()

            return render(request, 'view/TroubleHistory.html',{"info": alarm_list, 'counts': counts,'ps':ps,'all_counts':all_counts,'alarm_status_ok':alarm_status})
        elif start_time not in '' and end_time not in '' and "告警" in alarm_select:
            alarm_status=u'告警'
            qset =(
                Q(start_date__gte = start_time)&
                # Q(end_date__lte = end_time)&
                Q(alarm_status = alarm_select)
            )
            alarm_list = Aralminfo.objects.filter(qset).order_by('-start_date')
            counts = Aralminfo.objects.filter(qset).count()
            all_counts = Aralminfo.objects.all().count()

            return render(request, 'view/TroubleHistory.html',{"info":alarm_list, 'counts': counts,'ps':ps,'all_counts':all_counts,'alarm_status_ok':alarm_status})
        else:
            qset =(
                Q(alarm_status = '告警')&
                Q(alarm_status_ok = '')
            )
            alarm_status=u'告警'
            alarm_list = Aralminfo.objects.filter(qset).order_by('-start_date')
            counts = Aralminfo.objects.filter(qset).count()
            all_counts = Aralminfo.objects.all().count()

            return render(request, 'view/TroubleHistory.html',{"info": alarm_list, 'counts': counts,'ps':ps,'alarm_status_ok':alarm_status,'all_counts':all_counts})
    else:
        infos = Aralminfo.objects.all()[:100]
        all_counts = Aralminfo.objects.all().count()
        ret = ''
        return render(request,'view/TroubleHistory.html',{"info":infos,'all_counts':all_counts,'ret':ret,'ps':ps})


@login_required
def falcon_alarm_detail(request,pk):
    alarm_info = Aralminfo.objects.filter(id=int(pk))
    return render(request,'view/TroubleHisInfo.html',{'alarm_info':alarm_info})


@login_required
def echart(request):
    return render(request, 'view/source_map.html', locals())

@login_required
def TroubleGroup(request):
    alarm_group_sql = "select grp_name from grp;"
    alarm_group = db_falcon.select_table(alarm_group_sql)
    group_result_all = Roominfo.objects.all()
    if request.method=="GET" and len(request.GET.getlist('group'))>0:
        group = request.GET.getlist('group')
        # print len(request.GET.getlist('group'))
        if len(request.GET.getlist('group'))==1:
            group_result = Roominfo.objects.filter(cluster__contains=group[0])
        elif len(request.GET.getlist('group'))==2:
            sql = (Q(cluster__contains=group[0])|
                   Q(cluster__contains=group[1])
                   )
            group_result = Roominfo.objects.filter(sql)
        elif len(request.GET.getlist('group'))==3:
            sql = (Q(cluster__contains=group[0]) |
                   Q(cluster__contains=group[1]) |
                   Q(cluster__contains=group[2])
                   )
            group_result = Roominfo.objects.filter(sql)
        elif len(request.GET.getlist('group'))==4:
            sql = (Q(cluster__contains=group[0]) |
                   Q(cluster__contains=group[1]) |
                   Q(cluster__contains=group[2]) |
                   Q(cluster__contains=group[3])
                   )
            group_result = Roominfo.objects.filter(sql)
        elif len(request.GET.getlist('group'))==5:
            sql = (Q(cluster__contains=group[0]) |
                   Q(cluster__contains=group[1]) |
                   Q(cluster__contains=group[2]) |
                   Q(cluster__contains=group[3]) |
                   Q(cluster__contains=group[4])
                   )
            group_result = Roominfo.objects.filter(sql)
        return render(request, 'view/TroubleGroup.html',
                      {'alarm_group': alarm_group, 'group_result_all': group_result})

    return render(request,'view/TroubleGroup.html',{'alarm_group':alarm_group,'group_result_all':group_result_all})
