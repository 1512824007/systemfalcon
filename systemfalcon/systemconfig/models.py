# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class HostGroup(models.Model):
    host_group = models.CharField(max_length=50,null=False,blank=False,verbose_name=u'主机组名称',unique=True)
    def __unicode__(self):
        return self.host_group
    class Meta:
        verbose_name = u'主机分组表'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class Host(models.Model):
    hostname = models.CharField(max_length=100,verbose_name=u'主机名称',null=False,blank=False,unique=True)
    ip = models.CharField(max_length=100,verbose_name=u'主机IP',null=True,blank=True)
    host_room = models.CharField(max_length=100,verbose_name=u'机房名称',null=False,blank=False)
    host_cluster= models.CharField(max_length=100,verbose_name=u'业务线',null=True,blank=True)
    host_grp = models.ForeignKey('HostGroup',verbose_name=u'主机组名称',on_delete=models.PROTECT,blank=False,null=False)

    def __unicode__(self):
        return self.hostname

    class Meta:
        verbose_name = u'主机信息表'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class Tool(models.Model):
    tool_name = models.CharField(max_length=100,verbose_name=u'采集工具名称',null=False,blank=False)
    tool_host = models.ForeignKey('Host',verbose_name=u'主机信息',null=False,blank=False)
    tool_dir = models.CharField(max_length=500,verbose_name=u'采集工具存放路径',null=True,blank=True)
    tool_version = models.CharField(max_length=30,verbose_name=u'采集工具版本',null=True,blank=True)
    tool_context = models.TextField(max_length=500,verbose_name=u'采集工具说明',null=False,blank=False)
    def __unicode__(self):
        return self.tool_name

    class Meta:
        verbose_name = u'采集工具表'
        verbose_name_plural = verbose_name
        ordering = ['id']


class SLS(models.Model):
    sls_name = models.CharField(max_length=100,verbose_name=u'SLS文件名称',null=False,blank=False)
    sls_host = models.ForeignKey('Host',verbose_name=u'主机信息',null=False,blank=False)
    sls_dir = models.CharField(max_length=500,verbose_name=u'SLS文件存放路径',null=True,blank=True)
    sls_version = models.CharField(max_length=30,verbose_name=u'SLS版本',null=True,blank=True)
    sls_context = models.TextField(max_length=500,verbose_name=u'SLS文件备注说明',null=True,blank=True)
    def __unicode__(self):
        return self.sls_name

    class Meta:
        verbose_name = u'SLS文件存放表'
        verbose_name_plural = verbose_name
        ordering = ['id']


class Pack(models.Model):
    pack_name = models.CharField(max_length=100,verbose_name=u'参数包名称',null=False,blank=False)
    pack_host = models.ForeignKey('Host',verbose_name=u'主机信息',null=False,blank=False)
    pack_dir = models.CharField(max_length=500,verbose_name=u'参数包存放目录',null=True,blank=True)
    pack_context = models.CharField(max_length=100,null=True,blank=True,verbose_name=u'采集参数ID列表')
    pack_base_context = models.CharField(max_length=100,null=True,blank=True,verbose_name=u'采集基本参数ID列表')

    def __unicode__(self):
        return self.pack_name
    class Meta:
        verbose_name = u'采集参数包表'
        verbose_name_plural = verbose_name
        ordering = ['id']


class Pub_File(models.Model):
    pub_name = models.CharField(max_length=100,verbose_name=u'公共文件名称',null=False,blank=False,unique=True)
    pub_class = models.CharField(max_length=100,verbose_name=u'文件类型分类',null=False,blank=False)
    pub_dir = models.CharField(max_length=500,verbose_name=u'存放路径',null=True,blank=True)
    pub_parameter = models.ManyToManyField('Parameter')
    pub_file_name = models.CharField(max_length=100,verbose_name=u'文件名',null=True,blank=True)
    pub_context = models.TextField(max_length=500,verbose_name=u'采集工具说明',null=False,blank=False)
    def __unicode__(self):
        return self.pub_name

    class Meta:
        verbose_name = u'公共文件表'
        verbose_name_plural = verbose_name
        ordering = ['id']


class Private_Template(models.Model):
    private_template_name = models.CharField(max_length=100,verbose_name=u'模板名称',null=False,blank=False,unique=True)
    private_template_dir = models.CharField(max_length=500,verbose_name=u'模板存放路径',null=True,blank=True)
    private_template_file_name =models.CharField(max_length=100,verbose_name=u'模板文件名',null=True,blank=True)
    private_template_class = models.CharField(max_length=100,null=True,blank=True,verbose_name=u'类型分类')
    private_template_context = models.CharField(max_length=100,null=True,blank=True,verbose_name=u'模板说明')
    private_parameter = models.ManyToManyField('Parameter')

    def __unicode__(self):
        return self.private_template_name
    class Meta:
        verbose_name = u'私有模板表'
        verbose_name_plural = verbose_name
        ordering = ['id']


class Private_file(models.Model):
    private_name = models.CharField(max_length=100,verbose_name=u'名称',null=False,blank=False,unique=True)
    private_host = models.ForeignKey('Host',verbose_name=u'主机信息',null=False,blank=False,on_delete=models.PROTECT)
    private_dir = models.CharField(max_length=500,verbose_name=u'存放路径',null=True,blank=True)
    private_file_name =models.CharField(max_length=100,verbose_name=u'文件名',null=True,blank=True)
    private_class = models.CharField(max_length=100,null=True,blank=True,verbose_name=u'类型分类')
    private_context = models.CharField(max_length=100,null=True,blank=True,verbose_name=u'说明')

    def __unicode__(self):
        return self.private_name
    class Meta:
        verbose_name = u'私有文件表'
        verbose_name_plural = verbose_name
        ordering = ['id']


class Parameter(models.Model):
    parameter_context = models.CharField(max_length=500,verbose_name=u'采集参数内容',null=False,blank=False)
    parameter_default_id = models.IntegerField(verbose_name=u'缺省标记默认0',null=True,blank=True,default=0)
    parameter_name = models.CharField(max_length=100,verbose_name=u'采集参数名称',null=False,blank=False,unique=True)
    parameter_remark = models.CharField(max_length=100,verbose_name=u'采集参数说明',null=True,blank=True)
    parameter_group = models.ForeignKey('ParameterGroup',verbose_name=u'参数组',null=False,blank=False,on_delete=models.PROTECT)
    def __unicode__(self):
        return self.parameter_name
    class Meta:
        verbose_name = u'采集参数详情表'
        verbose_name_plural = verbose_name
        ordering = ['id']


class ParameterGroup(models.Model):
    param_group_name = models.CharField(max_length=30,verbose_name='参数组名称',null=False,blank=False,unique=True)
    param_group_content = models.CharField(max_length=500,verbose_name='参数组说明',null=False,blank=False)
    param_group_dir = models.CharField(max_length=100,verbose_name='plugin目录',null=False,blank=False)
    param_group_device_group = models.ManyToManyField('HostGroup')

    def __unicode__(self):
        return self.param_group_name
    class Meta:
        verbose_name=u'参数组管理表'
        verbose_name_plural = verbose_name
        ordering = ['id']