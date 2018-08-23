# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from celery import shared_task, platforms

from HcGraph import mysql
from top10 import mysql_falcon
from sysconf.models import GrpGroup,Module
from django.contrib.auth.models import User
import logging
from logging.handlers import TimedRotatingFileHandler


platforms.C_FORCE_ROOT = True
db = mysql.db_operate()
db_falcon = mysql_falcon.db_operate()


@shared_task
def send_register_email(email,rand_str="rand_str"):
    try:
        send_mail(u'gosun监控系统', u'\n\n注册验证码:' + rand_str, 'sys@gosun.com', email)
        return 'success!'
    except Exception as e:
        print(e)


@shared_task
def add_del_group_grp(user,gid,grp_id,device_old,grp_name):
    # 打印日志到文件中
    LOG_FILENAME = "/systemfalcon/systemfalcon/sysconf/log/ChangeLog.txt"
    logger = logging.getLogger()
    handler = TimedRotatingFileHandler(LOG_FILENAME,
                                       when='D', interval=1, backupCount=40,
                                       )
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.NOTSET)
    try:
        for i in list(eval(grp_id)):
            grp_sql = "insert into sysconf_grpgroup(group_id,grp)values({0},{1});".format(gid, int(i))
            grp_exist_sql = "select * from sysconf_grpgroup where group_id = {0} and grp ={1};".format(gid, int(i))
            if db.mysql_command(grp_exist_sql) == []:
                grp_name_sql = "select grp_name from grp where id={0}".format(int(i))
                devie_name = db_falcon.mysql_command(grp_name_sql)[0][0]
                db.mysql_command(grp_sql)
                logger.info("{0} add device_group {1} into group {2} ".format(user, devie_name.encode('UTF-8'),
                                                                              grp_name))
        for i in device_old:
            import operator
            if not any([operator.eq(i[0], x) for x in list(eval(grp_id))]):
                GrpGroup.objects.filter(grp=i[0]).delete()
                grp_name_sql = "select grp_name from grp where id={0}".format(int(i[0]))
                devie_name = db_falcon.mysql_command(grp_name_sql)[0][0]
                logger.info("{0} delete device_group {1} from group {2}".format(user, devie_name, grp_name))
        return 'success'
    except Exception as e:
        print(e)


@shared_task
def add_del_group_module(user,per_id,gid,ug_old,grp_name):
    # 打印日志到文件中
    LOG_FILENAME = "/systemfalcon/systemfalcon/sysconf/log/ChangeLog.txt"
    logger = logging.getLogger()
    handler = TimedRotatingFileHandler(LOG_FILENAME,
                                       when='D', interval=1, backupCount=40,
                                       )
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.NOTSET)
    try:
        for i in list(eval(per_id)):
            sql_exits = "select module_id,group_id from sysconf_module_group where module_id = {0} and group_id = {1};".format(int(i), int(gid))
            ug = db.mysql_command(sql_exits)
            if ug == []:
                sql_add = "insert into sysconf_module_group(module_id,group_id)values(%s,%s)" %(int(i), int(gid))
                db.mysql_command(sql_add)
                mod = Module.objects.filter(id=int(i))
                logger.info("{0} add module {1} into group {2}".format(user, mod, grp_name))
        for i in ug_old:
            import operator
            if not any([operator.eq(int(i[0]), int(x)) for x in list(eval(per_id))]):
                sql_del = "delete from sysconf_module_group where module_id = {0} and group_id = {1}".format(int(i[0]), int(gid))
                db.mysql_command(sql_del)
                mod = Module.objects.filter(id=int(i[0]))
                logger.info("{0} delete module {1} from group {2}".format(user, mod, grp_name))
        return 'success'
    except Exception as e:
        print(e)


@shared_task
def add_del_group_user(user,uid,gid,uid_old,grp_name):
    # 打印日志到文件中
    LOG_FILENAME = "/systemfalcon/systemfalcon/sysconf/log/ChangeLog.txt"
    logger = logging.getLogger()
    handler = TimedRotatingFileHandler(LOG_FILENAME,
                                       when='D', interval=1, backupCount=40,
                                       )
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.NOTSET)
    try:
        for i in list(eval(uid)):
            sql_exits = "select user_id,group_id from auth_user_groups where user_id = {0} and group_id = {1};".format(int(i), int(gid))
            ug = db.mysql_command(sql_exits)
            if ug == []:
                sql_add = "insert into auth_user_groups(user_id,group_id)values(%s,%s)" %(int(i), int(gid))
                db.mysql_command(sql_add)
                u_name = User.objects.get(id=i).username
                logger.info("{0} add user {1} into group {2}".format(user, u_name, grp_name))
        for i in uid_old:
            import operator
            if not any([operator.eq(int(i[0]), int(x)) for x in list(eval(uid))]):
                sql_del = "delete from auth_user_groups where user_id = {0} and group_id = {1}".format(int(i[0]), int(gid))
                db.mysql_command(sql_del)
                u_name = User.objects.get(id=int(i[0])).username
                logger.info("{0} delete user {1} from group {2}".format(user, u_name, grp_name))
        return 'success'
    except Exception as e:
        print(e)