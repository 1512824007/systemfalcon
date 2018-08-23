# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import Group

# Create your models here.


class room_bandwidth(models.Model):
    province = models.TextField(max_length=200,null=True,verbose_name=u'省份')
    operator = models.CharField(max_length=200,null=True,verbose_name=u'运营商')
    idc_name = models.CharField(max_length=200,null=True,verbose_name=u'CDN节点名称（机房）')
    speed = models.CharField(max_length=100,null=True,verbose_name=u'带宽（M）')
    available_speed = models.CharField(max_length=100,null=True,verbose_name=u'可用带宽（M）')
    bottom_speed = models.CharField(max_length=100,null=True,verbose_name=u'保底（M）')
    remarks = models.CharField(max_length=500, null=True, verbose_name=u'备注')

    def __unicode__(self):
        return self.idc_name

    class Meta:
        verbose_name = u'机房带宽'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class Module(models.Model):
    module_name = models.CharField(max_length=200,null=True,verbose_name=u'模块名称')
    remarks = models.CharField(max_length=500, null=True, verbose_name=u'备注')

    def __unicode__(self):
        return self.module_name

    class Meta:
        verbose_name = u'模块（页面板块）'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class Module_group(models.Model):
    module = models.ForeignKey(Module)
    group = models.ForeignKey(Group)

    class Meta:
        verbose_name = u'模块与组关系表'
        verbose_name_plural = verbose_name
        ordering = ['-id']

class GrpGroup(models.Model):
    grp = models.CharField(max_length=100, null=True, verbose_name=u'设备组')
    group = models.ForeignKey(Group)

    class Meta:
        verbose_name = u'设备组与用户组关系表'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class ClassMod(models.Model):
    class_mod = models.CharField(max_length=100, null=True, verbose_name=u'类模块')
    parameter = models.CharField(max_length=200, null=True, verbose_name=u'参数')
    result = models.CharField(max_length=200, null=True, verbose_name=u'返回结果')
    api = models.CharField(max_length=200, null=True, verbose_name=u'调用方式')
    remarks = models.CharField(max_length=500, null=True, verbose_name=u'备注')

    class Meta:
        verbose_name = u'接口或模块'
        verbose_name_plural = verbose_name
        ordering = ['-id']