# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Alarm(models.Model):
    json = models.TextField(verbose_name=u'告警结果',null=True)

    def __unicode__(self):
        return self.json


class Roominfo(models.Model):
    hostname = models.CharField(max_length=200,null=True,verbose_name=u'主机名称')
    room = models.CharField(max_length=200,null=True,verbose_name=u'机房名称')
    ip = models.CharField(max_length=200,null=True,verbose_name=u'IP')
    cluster = models.CharField(max_length=500,null=True,verbose_name=u'集群业务名称')
    aralm = models.CharField(max_length=300,null=True,verbose_name=u'告警信息')
    date = models.CharField(max_length=100,null=True,verbose_name=u'时间')
    counts = models.IntegerField(null=True,verbose_name=u'告警数量统计')

    metric = models.CharField(max_length=128,null=True,blank=True,verbose_name=u'监控项')
    event_id = models.CharField(max_length=100,null=True,blank=True,verbose_name=u'告警事件ID')

    def __unicode__(self):
        return self.hostname

    class Meta:
        verbose_name = u'告警列表'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class Roomname(models.Model):
    ext_info = models.TextField(null=True,verbose_name=u'扩展信息')
    created_time = models.DateTimeField(null=True,verbose_name=u'创建时间')
    name = models.CharField(max_length=30,null=True,verbose_name=u'机房名称',unique=True)
    abbr_name = models.CharField(max_length=15,null=True,verbose_name=u'简称',unique=True)
    country = models.CharField(max_length=5,null=True,verbose_name=u'国家')
    province = models.CharField(max_length=5,null=True,verbose_name=u'省份')
    city = models.CharField(max_length=5,null=True,verbose_name=u'城市')
    address = models.CharField(max_length=100,null=True,verbose_name=u'地址')
    phone = models.CharField(max_length=20,null=True,verbose_name=u'电话')
    email = models.CharField(max_length=254,null=True,verbose_name=u'邮箱')
    room_number = models.CharField(max_length=20,null=True,verbose_name=u'地方编号')

    def __unicode__(self):
        return self.name


    class Meta:
        verbose_name=u'机房信息'


class Aralminfo(models.Model):
    hostname = models.CharField(max_length=200,null=True,verbose_name=u'主机名称')
    room = models.CharField(max_length=200,null=True,verbose_name=u'机房名称')
    ip = models.CharField(max_length=200,null=True,verbose_name=u'IP')
    cluster = models.CharField(max_length=500,null=True,verbose_name=u'集群业务名称')
    aralm = models.CharField(max_length=300,null=True,verbose_name=u'告警信息')
    start_date = models.DateTimeField(max_length=100,null=True,verbose_name=u'时间')
    counts = models.IntegerField(null=True,verbose_name=u'告警数量统计')
    alarm_status = models.CharField(max_length=10,null=True,blank=True,verbose_name=u'告警状态')
    end_date = models.DateTimeField(max_length=100,null=True,blank=True,verbose_name=u'时间')
    alarm_status_ok = models.CharField(max_length=10,null=True,blank=True,verbose_name=u'告警状态')
    metric = models.CharField(max_length=128,null=True,blank=True,verbose_name=u'监控项')
    event_id = models.CharField(max_length=100,null=True,blank=True,verbose_name=u'告警事件ID')
    remarks = models.TextField(max_length=2000,blank=True,null=True,verbose_name=u'备注信息(LOG)')


    def __unicode__(self):
        return self.hostname

    class Meta:
        verbose_name = u'历史告警'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class Alarm_op(models.Model):
    alarm_host_id = models.IntegerField(null=False,verbose_name=u'告警主机ID')
    alarm_host = models.CharField(max_length=100,null=False,blank=False,verbose_name=u'主机名称')
    alarm = models.CharField(max_length=1000,null=False,blank=False,verbose_name=u'告警信息')
    alarm_operation = models.TextField(null=True,blank=True,verbose_name=u'操作处理信息')
    alarm_date = models.DateTimeField(auto_now_add=True,verbose_name=u'更新时间')

    def __unicode__(self):
        return self.alarm_host

    class Meta:
        verbose_name = u'故障设备操作记录'
        verbose_name_plural =verbose_name
        ordering = ['-id']

# System configuration manage
