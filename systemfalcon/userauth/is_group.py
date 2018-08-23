#coding:utf8
from django.http import HttpResponse
from django.contrib.auth.models import Group


def is_group(*arg):
    def group(func):
        def wrapper(*args, **kw):
            u = args[0].user
            group = Group.objects.filter(user=u).values_list('name')
            init = 0
            for i in group:
                if arg[0] == i[0]:
                    init += 1
                else:
                    continue
            if init > 0:
                return func(*args, **kw)
            else:
                return HttpResponse(u'对不起，您没有 {0} 组权限'.format(arg[0]))
        return wrapper
    return group

