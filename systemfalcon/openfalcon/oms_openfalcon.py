# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mysql,mysql_falcon,mysql_oms
import pymysql
import time

class Oms_Openfalcon:
    '''open-falcon and oms '''

    sql_db = mysql.db_operate()
    falcon_db = mysql_falcon.db_operate()
    oms_db = mysql_oms.db_operate()
    def __init__(self,url):
        self.url = url

    def open_falcon(self):
        oms_sql ="select  d.abbr_name from " \
                 "device_server a ,business_clusterserver b,business_cluster c ,business_project d where a.id=b.device_id and" \
                 " b.cluster_id=c.id and c.project_id=d.id and a.hostname='%s';"%(self.url)
        oms_info = Oms_Openfalcon.oms_db.select_count_table(oms_sql)
        ip_sql = "select b.ip from device_server a,device_serverinterface b where a.id=b.device_id and b.ip not like '10.32.%%' and  a.hostname='%s' limit 1;"%(self.url)
        ip_info = Oms_Openfalcon.oms_db.select_count_table(ip_sql)
        if len(oms_info) > 0:
            if len(oms_info) > 1:
                try:
                    print(u"more cluster")
                    cluster_join = "'"+"','".join(oms_info)+"'"
                    oms_cluster = "select DISTINCT grp_name_id from oms_openfalcon where abbr_name in (%s);" % (cluster_join)
                    print(oms_cluster)
                    db = Oms_Openfalcon.sql_db.select_count_table(oms_cluster)
                    if db[0]:
                        print(db[0])
                        try:
                            select = "select count(hostname) from host where hostname='%s';"%(self.url)
                            count = Oms_Openfalcon.falcon_db.select_count_table(select)
                            if count[0] < 1:
                                sql = "insert into host(hostname,ip,agent_version,plugin_version) VALUES ('%s','%s','5.1.1','plugin not enabled');" % (self.url, ip_info[0])
                                try:
                                    Oms_Openfalcon.falcon_db.mysql_command(sql)
                                    hostid = "select id from host where hostname='%s';"%(self.url)
                                    host_id = Oms_Openfalcon.falcon_db.select_count_table(hostid)
                                    grp_host = "insert into grp_host(grp_id,host_id) VALUES('%s','%s')" % (db[0], host_id[0])
                                    Oms_Openfalcon.falcon_db.mysql_command(grp_host)
                                    update = "update emp_hostname set status=1 where hostname='%s';"%(self.url)
                                    Oms_Openfalcon.sql_db.mysql_command(update)
                                    print(grp_host)
                                    print(update)
                                    print(u'Add open_falcon seccuss !!')
                                except:
                                    print("Add Error!!!")
                                    pass
                            elif count[0] >= 1:
                                select ="select host_id from grp_host where host_id in(select id from host where hostname='%s');" % (self.url)
                                host_id = Oms_Openfalcon.falcon_db.select_count_table(select)
                                if len(host_id)>0:
                                    update = "update emp_hostname set status=1 where hostname='%s';" % (self.url)
                                    Oms_Openfalcon.sql_db.mysql_command(update)
                                    print(u"The host has been added to open_falcon_monitor.")
                                else:
                                    hostid ="select id from host where hostname='%s';" % (self.url)
                                    h_id = Oms_Openfalcon.falcon_db.select_count_table(hostid)
                                    grp_host = "insert into grp_host(grp_id,host_id) VALUES('%s','%s');" % (db[0], h_id[0])
                                    Oms_Openfalcon.falcon_db.mysql_command(grp_host)
                                    update = "update emp_hostname set status=1 where hostname='%s';" % (self.url)
                                    Oms_Openfalcon.sql_db.mysql_command(update)
                                    print(grp_host)
                                    print(update)
                                    print(u'table group_host update seccuss!')

                        except pymysql.Error as e:
                            print(e)
                            pass
                    elif db[0] == None:
                        print(u'TABLE oms_openfalcon in grp_name_id is null,please manage')
                    else:
                        print(u"No add open_falon monitor cluster")
                        pass

                except Exception as e:
                    print(e)
                    print('Error warning!')
                    pass

            elif len(oms_info) == 1:
                try:
                    print(u'One cluster')
                    oms_cluster = "select DISTINCT grp_name_id from oms_openfalcon where abbr_name in ('%s');" % (oms_info[0])
                    db = Oms_Openfalcon.sql_db.select_count_table(oms_cluster)
                    if db[0]:
                        print(db[0])
                        try:
                            select = "select count(hostname) from host where hostname='%s';"%(self.url)
                            count = Oms_Openfalcon.falcon_db.select_count_table(select)
                            if count[0] < 1:
                                sql = "insert into host(hostname,ip,agent_version,plugin_version) VALUES ('%s','%s','5.1.1','plugin not enabled');" % (self.url, ip_info[0])
                                try:
                                    Oms_Openfalcon.falcon_db.mysql_command(sql)
                                    hostid = "select id from host where hostname='%s';"%(self.url)
                                    host_id = Oms_Openfalcon.falcon_db.select_count_table(hostid)
                                    grp_host = "insert into grp_host(grp_id,host_id) VALUES('%s','%s')" % (db[0], host_id[0])
                                    Oms_Openfalcon.falcon_db.mysql_command(grp_host)
                                    update = "update emp_hostname set status=1 where hostname='%s';"%(self.url)
                                    print(grp_host)
                                    print(update)
                                    Oms_Openfalcon.sql_db.mysql_command(update)
                                    print(u'Add open_falcon seccuss !!')
                                except Exception:
                                    print("Add Error!!!")
                                    pass
                            elif count[0] >= 1:
                                select ="select host_id from grp_host where host_id in(select id from host where hostname='%s');" % (self.url)
                                host_id = Oms_Openfalcon.falcon_db.select_count_table(select)
                                if len(host_id)>0:
                                    update = "update emp_hostname set status=1 where hostname='%s';" % (self.url)
                                    Oms_Openfalcon.sql_db.mysql_command(update)
                                    print(u"The host has been added to open_falcon_monitor.")
                                else:
                                    hostid ="select id from host where hostname='%s';" % (self.url)
                                    h_id = Oms_Openfalcon.falcon_db.select_count_table(hostid)
                                    grp_host = "insert into grp_host(grp_id,host_id) VALUES('%s','%s');" % (db[0], h_id[0])
                                    Oms_Openfalcon.falcon_db.mysql_command(grp_host)
                                    update = "update emp_hostname set status=1 where hostname='%s';" % (self.url)
                                    Oms_Openfalcon.sql_db.mysql_command(update)
                                    print grp_host
                                    print update
                                    print u'table group_host update seccuss!'

                        except Exception as e:
                            print(e)
                            pass
                    elif db[0] == None:
                        print(u'TABLE oms_openfalcon in grp_name_id is null,please manage')
                    else:
                        print(u"No add open_falon monitor cluster")
                        pass
                except Exception as e:
                    print(e)
                    print('Error warning!')
                    pass
        else:
            print(u"oms cluster data is null")
            pass


    def open_falcon_delte(self):
        try:
            hostid = "select id from host where hostname='%s';" % (self.url)
            host_id = Oms_Openfalcon.falcon_db.select_count_table(hostid)

            grp_id = "select host_id from grp_host where host_id in (select id from host where hostname='%s');" % (self.url)
            grp_host_id = Oms_Openfalcon.falcon_db.select_count_table(grp_id)

            if len(host_id) or len(grp_host_id):
                grp_host = "delete from  grp_host where host_id='%s'" % (host_id[0])
                host = "delete from  host where id='%s'" % (host_id[0])
                Oms_Openfalcon.falcon_db.mysql_command(grp_host)
                Oms_Openfalcon.falcon_db.mysql_command(host)
                update = "update emp_hostname set status=1 where hostname='%s';" % (self.url)
                Oms_Openfalcon.sql_db.mysql_command(update)
                print(host)
                print(grp_host)
                print(self.url,u'Delete seccuss')
            else:
                update = "update emp_hostname set status=1 where hostname='%s';" % (self.url)
                Oms_Openfalcon.sql_db.mysql_command(update)
                print(self.url)
                print(u'The hostname is out in open_falcon monitor')
        except pymysql.Error as e:
            print(e)
            pass


    def oms_nocluster_delte(self):
        '''清理小米监控，被nocluster函数调用'''
        try:
            hostid = "select id from host where hostname='%s';" % (self.url)
            host_id = Oms_Openfalcon.falcon_db.select_count_table(hostid)

            grp_id = "select host_id from grp_host where host_id in (select id from host where hostname='%s');" % (self.url)
            grp_host_id = Oms_Openfalcon.falcon_db.select_count_table(grp_id)

            print(host_id)
            print(grp_host_id)

            if len(host_id) or len(grp_host_id):
                print('-----------------------------------------')
                grp_host = "delete from  grp_host where host_id='%s'" % (host_id[0])
                host = "delete from  host where id='%s'" % (host_id[0])
                print(grp_host,host)
                Oms_Openfalcon.falcon_db.mysql_command(grp_host)
                Oms_Openfalcon.falcon_db.mysql_command(host)
                print(self.url,u'Delete seccuss')
            else:
                print('------------------------------------------')
                print(self.url)
                print(u'The hostname is out in open_falcon monitor')
        except pymysql.Error as e:
            print(e)
            pass

    def nocluster(self):
        '''清理小米监控中，oms系统中没有业务线的主机信息'''
        try:
            no_cluster = "select hostname from device_server where id not in(select distinct a.device_id from business_clusterserver a,device_server b where a.device_id=b.id);"
            nodata = Oms_Openfalcon.oms_db.select_table(no_cluster)
            # i = 0
            for reslut in nodata:
                # print reslut
                open_falcon = Oms_Openfalcon(reslut)
                open_falcon.oms_nocluster_delte()
                # i += 1
            # print i

        except pymysql.Error as e:
            print(e)
            pass


def sync_oms():
    print('start time:',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    cls = Oms_Openfalcon('')
    cls.nocluster()
    try:
        delete = "delete from emp_hostname where hostname is NULL;"
        Oms_Openfalcon.sql_db.mysql_command(delete)
        sql = "select hostname from emp_hostname where status=0 and hostname is not NULL;"
        db = Oms_Openfalcon.sql_db.select_table(sql)
        if len(db)>0:
            for reslut in db:
                print(reslut)
                oms = Oms_Openfalcon(reslut)
                oms.open_falcon()
        sql1 = "select hostname from emp_hostname where status=2 and hostname is not NULL;"
        db1 = Oms_Openfalcon.sql_db.select_table(sql1)
        print(len(db1))
        if len(db1)>0:
            for reslut1 in db1:
                print(reslut1)
                open_falcon = Oms_Openfalcon(reslut1)
                open_falcon.open_falcon_delte()
    except pymysql.Error as e:
        print(e)
        pass
    print('end time:',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
