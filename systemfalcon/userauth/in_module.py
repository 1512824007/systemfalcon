#coding:utf8
from django.http import HttpResponse
from django.contrib.auth.models import Group
from sysconf.models import Module, GrpGroup, Module_group
from openfalcon import mysql_falcon
#import time

db_falcon = mysql_falcon.db_operate()

def in_module(request,*args, **kw):
    u = request.user
    groupid = Group.objects.filter(user=u).values_list('id')
    init = 0
    for j in groupid:
        mod = Module.objects.filter(module_group__group=int(j[0])).values_list('module_name')
        for i in mod:
            if args[0] == i[0]:
                init += 1
            else:
                continue
    if init > 0:
        return 1
    else:
        return 0
        #return HttpResponse(u'对不起，您所属组 不在 {0} 模块中'.format(arg[0]))


def return_device_group(request,*args, **kw):
    u = request.user
    try:
        groupid = Group.objects.filter(user=u).values_list('id')
        mod_id = ()
        mod = []
        for j in groupid:
            try:
                grp = GrpGroup.objects.filter(group=int(j[0])).values_list('grp')
                for i in  grp:
                    mod_id += (int(i[0]),)
            except Exception as e:
                print(e)
                continue
        grp_sql = "select grp_name from grp where id in {0}".format(mod_id)
        cluster_name = db_falcon.mysql_command(grp_sql)
        for i in cluster_name:
            mod +=[i[0].encode('UTF-8')]
        return list(set(mod))
    except Exception as e:
        print(e)
        return []

def return_module(request,*args, **kw):
    u = request.user
    if args[0]:
        u = args[0]
    try:
        groupid = Group.objects.filter(user=u).values_list('id')
        mod = []
        for j in groupid:
            try:
                module = Module_group.objects.filter(group__id=int(j[0])).values_list('module')
                for i in  module:
                    module_name = Module.objects.get(id=i[0]).module_name
                    mod +=[module_name]
            except Exception as e:
                print e
                continue
        return list(set(mod))
    except Exception as e:
        return []

