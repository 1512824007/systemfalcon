#!/usr/bin/env python
# -*- coding:utf-8 -*-
from lxml import html
import json,re,urllib2
import requests
import mysql
import mysql_falcon
import time,datetime

db = mysql.op_mysql()
db_openfalcon = mysql_falcon.db_operate()

def info():
    page = requests.get('http://192.168.41.132:8081/portal/alarm-dash/case')
    info = html.fromstring(page.text)
    hosts = info.xpath('//div [@class="alarm"]/text()')
    alarm = info.xpath('//span [@style="padding-left:17px;"]/text()')
    datetime = info.xpath('//span [@class="orange"]/text()')
    alarm_id = info.xpath('//div/input[@type="checkbox"]/@alarm')

    hosts_info = '\n'.join(hosts).encode('utf-8')
    alarm_info = '\n'.join(alarm).encode('utf-8')
    datetime_info = '\n'.join(datetime).encode('utf-8')
    alarm_id_info = '\n'.join(alarm_id).encode('utf-8')
	
    """告警主机ID信息"""
    open('./alarm_id', 'w').write("")
    f = open('./alarm_id', 'a')
    f.write(alarm_id_info + '\n')
    f.close()

    """告警监控项"""
    open('./monitor_info', 'w').write("")
    for i in hosts:
        infos = str(i).strip()
        name = infos.split()
        if name:
            alarm_infos = name[2].split('/')
            #print alarm_infos[1]
            f = open('./monitor_info','a')
            f.write(alarm_infos[1]+'\n')
            f.close()

    """告警主机信息"""
    open('./hosts', 'w').write("")
    for i in hosts:
        infos =  str(i).strip()
        f1 = infos.split()
        if f1:
            f2 =  f1[0][:-3]
            f = open('./hosts', 'a')
            f.write(f2+'\n')
            f.close()

    """告警业务"""
    open('./alarm','w').write("")
    f = open('./alarm','a')
    f.write(alarm_info)
    f.close()

    """告警过去时间"""
    open('./datetime','w').write("")
    f = open('./datetime','a')
    f.write(datetime_info+'\n')
    f.close()

    """处理告警信息"""
    file = open('./alarm', 'r')
    open('./temp', 'w')
    for f in file.readlines():
        f1 = f.startswith("all")
        if f1:
            fi = open('./temp', 'a')
            fi.write(f)
        else:
            pass


    """处理业务线信息"""
    file = open('./hosts', 'r')
    open('./cluster', 'w')
    for f in file.readlines():
        if f:
            sql = "select grp_name from grp where id in (select grp_id from grp_host where host_id in(select id from host where hostname='%s'));" %(f.strip())
            #print sql
            openfalcom = db_openfalcon.select_count_table(sql)
            cluster = ''.join(openfalcom).encode('utf-8')
            if openfalcom:
                fi = open('./cluster', 'a')
                fi.write(cluster+"\n")
            else:
                fi = open('./cluster', 'a')
                fi.write("无业务"+'\n')
        else:
            pass 

def read():
    # os.system('python join.py hosts')
    file = open('./temp','r')
    file1 = open('./hosts','r')
    file2 = open('./datetime','r')
    open('./json','w')
    json = open('./json','a')
    json.write('{ "告警":[')
    while 1:
        json.write("{")
        line = file.readline().strip()
        line1 = file1.readline().strip()
        line2 = file2.readline().strip()
        # print '"host":'+'"'+line1.strip(), line.strip(),line2.strip()+'"'
        json.write('"room":'+'"'+line1.strip()+line.strip()+line2.strip()+'"')
        json.write("},")
        if not line and not line1 and not line2:
            break
        pass
    json.write("]}")
    json.close()

def writemysql():
    clear = "delete from openfalcon_roominfo;"
    db.mysql_command(clear)
    file = open('./temp', 'r')
    file1 = open('./hosts', 'r')
    file2 = open('./datetime', 'r')
    file3 = open('./cluster', 'r')
    file4 = open('./oms', 'r')
    file5 = open('./monitor_info', 'r')
    file6 = open('./alarm_id', 'r')
    while 1:
        line = file.readline().strip()
        line1 = file1.readline().strip()
        line2 = file2.readline().strip()
        line3 = file3.readline().strip()
        line4 = file4.readline().split()
        line5 = file5.readline().strip()
	line6 = file6.readline().strip()
        if len(line1)>0:
            sql = "insert into openfalcon_roominfo(room,hostname,ip,cluster,aralm,date,counts,metric,event_id) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" %(line4[0].strip(),line1.strip(),line4[1].strip(),line3.strip(),line.strip(),line2.strip(),1,line5.strip(),line6.strip())
            db.mysql_command(sql)
            print line2.strip()
            # db.mysql_command(sql_alarm)
            # print line2.strip()
            if 'day' in line2.strip():
                '''天为单位'''
                date = datetime.datetime.now() - datetime.timedelta(days = int(line2.strip().split()[0]))
                times = date.strftime('%Y-%m-%d %H:%M:%S')
                select_alarm_pro = "select count(1) from openfalcon_aralminfo WHERE room = '%s' and hostname = '%s' and ip = '%s' and cluster = '%s' and aralm ='%s' and alarm_status = '告警' and alarm_status_ok = '';" % (line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip())
                select_alarm_ok = "select count(1) from openfalcon_aralminfo WHERE room = '%s' and hostname = '%s' and ip = '%s' and cluster = '%s' and aralm ='%s' and alarm_status_ok = '恢复' and alarm_status = '告警';" % (line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip())
                problem = db.select_room_table(select_alarm_pro)
                print problem[0]
                ok = db.select_room_table(select_alarm_ok)
                if problem[0] <1:
                    sql_alarm = "insert into openfalcon_aralminfo(room,hostname,ip,cluster,aralm,start_date,counts,alarm_status,alarm_status_ok,metric,event_id) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip(), times, 1,'告警','',line5.strip(),line6.strip())
                    db.mysql_command(sql_alarm)
                    print '[days] Alarm add success!,alarm info is new!!!'
                elif problem[0]>0:
                    print '[days] Alarm info include is haved ,skip!!'
                else:
                    pass

            elif 'hour' in line2.strip():
                '''小时为单位'''
                date = datetime.datetime.now() - datetime.timedelta(hours=int(line2.strip().split()[0]))
                times = date.strftime('%Y-%m-%d %H:%M:%S')
                select_alarm_pro = "select count(1) from openfalcon_aralminfo WHERE room = '%s' and hostname = '%s' and ip = '%s' and cluster = '%s' and aralm ='%s' and alarm_status = '告警' and alarm_status_ok = '';" % (
                line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip())
                select_alarm_ok = "select count(1) from openfalcon_aralminfo WHERE room = '%s' and hostname = '%s' and ip = '%s' and cluster = '%s' and aralm ='%s' and alarm_status_ok = '恢复' and alarm_status = '告警';" % (
                line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip())
                problem = db.select_room_table(select_alarm_pro)
                print problem[0]
                ok = db.select_room_table(select_alarm_ok)
                if problem[0] < 1:
                    sql_alarm = "insert into openfalcon_aralminfo(room,hostname,ip,cluster,aralm,start_date,counts,alarm_status,alarm_status_ok,metric,event_id) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                    line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip(), times, 1, '告警', '',line5.strip(),line6.strip())
                    db.mysql_command(sql_alarm)
                    print '[hours] Alarm add success!,alarm info is new!!!'
                elif problem[0] >0:
                    print '[hours] Alarm info include is haved ,skip!!'
                else:
                    pass

            elif 'minute' in line2.strip():
                '''分钟为单位'''
                date = datetime.datetime.now() - datetime.timedelta(minutes=int(line2.strip().split()[0]))
                times = date.strftime('%Y-%m-%d %H:%M:%S')
                select_alarm_pro = "select count(1) from openfalcon_aralminfo WHERE room = '%s' and hostname = '%s' and ip = '%s' and cluster = '%s' and aralm ='%s' and alarm_status = '告警' and alarm_status_ok = '';" % (
                line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip())
                select_alarm_ok = "select count(1) from openfalcon_aralminfo WHERE room = '%s' and hostname = '%s' and ip = '%s' and cluster = '%s' and aralm ='%s' and alarm_status_ok = '恢复' and alarm_status = '告警';" % (
                line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip())
                problem = db.select_room_table(select_alarm_pro)
                print problem[0]
                ok = db.select_room_table(select_alarm_ok)
                if problem[0] < 1:
                    sql_alarm = "insert into openfalcon_aralminfo(room,hostname,ip,cluster,aralm,start_date,counts,alarm_status,alarm_status_ok,metric,event_id) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                    line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip(), times, 1, '告警', '',line5.strip(),line6.strip())
                    db.mysql_command(sql_alarm)
                    print '[minutes] Alarm add success!,alarm info is new!!!'
                elif problem[0] >0:
                    print '[minutes] Alarm info include is haved ,skip!!'
                else:
                    pass

            elif 'just' in line2.strip():
                '''秒为单位'''
                date = datetime.datetime.now()
                times = date.strftime('%Y-%m-%d %H:%M:%S')
                select_alarm_pro = "select count(1) from openfalcon_aralminfo WHERE room = '%s' and hostname = '%s' and ip = '%s' and cluster = '%s' and aralm ='%s' and alarm_status = '告警' and alarm_status_ok = '';" % (
                line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip())
                select_alarm_ok = "select count(1) from openfalcon_aralminfo WHERE room = '%s' and hostname = '%s' and ip = '%s' and cluster = '%s' and aralm ='%s' and alarm_status_ok = '恢复' and alarm_status = '告警';" % (
                line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip())
                problem = db.select_room_table(select_alarm_pro)
                ok = db.select_room_table(select_alarm_ok)
                if problem[0] < 1:
                    sql_alarm = "insert into openfalcon_aralminfo(room,hostname,ip,cluster,aralm,start_date,counts,alarm_status,alarm_status_ok,metric,event_id) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                    line4[0].strip(), line1.strip(), line4[1].strip(), line3.strip(), line.strip(), times, 1, '告警', '',line5.strip(),line6.strip())
                    db.mysql_command(sql_alarm)
                    print '[just] Alarm add success!,alarm info is new!!!'
                elif problem[0] > 0:
                    print '[just] Alarm info include is haved ,skip!!'
                else:
                    pass

        if not line and not line1:
            break
            pass

def alarm_ok():
    '''告警恢复'''
    # select_alarm_temp = "select hostname from openfalcon_aralminfo_temp a where a.hostname not in (select hostname from openfalcon_roominfo);"
    # temp = db.select_room_table(select_alarm_temp)
    try:
        date = datetime.datetime.now()
        times = date.strftime('%Y-%m-%d %H:%M:%S')
        alarm_ok_sql ="select id from openfalcon_aralminfo c where c.id in (SELECT  a.id FROM  openfalcon_aralminfo a left join openfalcon_roominfo b ON   a.hostname = b.hostname    AND a.aralm=b.aralm and a.room = b.room  where b.id is null) and c.alarm_status_ok='';"
        ids = db.select_room_table(alarm_ok_sql)
        for id in ids:
            ok_sql = "update openfalcon_aralminfo set alarm_status_ok='恢复',end_date='%s' where id='%d'"%(times,id)
            db.mysql_command(ok_sql)
            print 'OK is alarm!!'
        print 'Alarm ok,time:',times
    except Exception:
        print Exception



def result():
    sql = "select room,hostname,ip,cluster,aralm,date,count(counts) from openfalcon_roominfo group by room;"
    sqlinfo = db.select_count_table(sql)
    open('./json', 'w')
    json = open('./json', 'a')
    json.write('[')
    for row in sqlinfo:
        row1 = ''.join(row[0]).encode('utf-8')
        row7 = ''.join(str(row[6]))
        json.write("{")
        json.write('"name":' + '"' + row1 + '",')
        json.write('"value":' + '"' + row7 + '"')
        json.write("},")
    json.write("]")
    json.close()
    '''得到最终结果'''
    info = open('./json', 'r')
    rows = info.readlines()
    rows_info = ''.join(rows)
    result = rows_info.replace(',]', ']')
    #print result
    rs = open('/systemfalcon/systemfalcon/static/alarm/result','w')
    rs.write(result)
    rs.close()

def alarm_class():
    """告警分类图表"""
    sql = "select metric,hostname,ip,cluster,aralm,date,count(counts) from openfalcon_roominfo group by metric;"
    sqlinfo = db.select_count_table(sql)
    open('./json_class', 'w')
    json = open('./json_class', 'a')
    json.write('[')
    for row in sqlinfo:
        row1 = ''.join(row[0]).encode('utf-8')
        row7 = ''.join(str(row[6]))
        json.write("{")
        json.write('"name":' + '"' + row1 + '",')
        json.write('"value":' + '"' + row7 + '"')
        json.write("},")
    json.write("]")
    json.close()
    '''得到最终结果'''
    info = open('./json_class', 'r')
    rows = info.readlines()
    rows_info = ''.join(rows)
    result = rows_info.replace(',]', ']')
    #print result
    rs = open('/systemfalcon/systemfalcon/static/alarm/result_class','w')
    rs.write(result)
    rs.close()


def alarm():
    sql = "select room,hostname,ip,cluster,aralm,date,count(counts) from openfalcon_roominfo group by room;"
    room = "select name from openfalcon_roomname where name not in(select room from openfalcon_roominfo);"
    sqlinfo = db.select_count_table(sql)
    room_name = db.select_room_table(room)
    open('./json_alarm', 'w')
    json = open('./json_alarm', 'a')
    json.write('[')
    for row in sqlinfo:
        row1 = ''.join(row[0]).encode('utf-8')
        row7 = ''.join(str(row[6]))
        json.write("{")
        json.write('"name":' + '"' + row1.strip() + '",')
        json.write('"value":' + '"' + row7 + '"')
        json.write("},")
    for name in room_name:
        name_row = ''.join(name).encode('utf-8')
        json.write("{")
        json.write('"name":' + '"' + name_row.strip() + '",')
        json.write('"value":' + '"0"')
        json.write("},")
    json.write("]")
    json.close()
    '''得到最终结果'''
    info = open('./json_alarm', 'r')
    rows = info.readlines()
    rows_info = ''.join(rows)
    result = rows_info.replace(',]', ']')
    #print result
    rs = open('/systemfalcon/systemfalcon/static/alarm/result_alarm','w')
    rs.write(result)
    rs.close()


class Oms_Openfalcon:
    '''open-falcon and oms '''

    sql_db = mysql.op_mysql()

    def __init__(self, url):
        self.url = url

    def open_falcon(self):
        request = urllib2.Request(self.url)
        request.add_header('Authorization', 'Token 4329a4b7656f11e89c19000c2971dd94')
        response = urllib2.urlopen(request)
        oms = response.read()
        oms_info = json.loads(oms)
        f = open('./oms', 'a')
        if len(oms_info) > 0:
            hostname = oms_info['hostname']
            ip = ''.join(oms_info['ip']).encode('utf-8')
            cluster = oms_info['cluster']
            room_name = ''.join(oms_info['room_name']).encode('utf-8')
            # print room_name
            cluster_re = "".join(cluster).split(',')
            # print cluster
            f.write(room_name +' ' +ip  + '\n')
        else:
            # print u"data is null"
            f.write("已下架"+" " + "无" + '\n')



if __name__ == '__main__':
    info()
    f = open('./oms','w')
    with open('./hosts') as f:
        for r in  f.readlines():
            urls = "http://122.228.213.76/inventory/device/api_monitor/openserverinfo?dev_name=%s" % (r)
            # print urls
            oms = Oms_Openfalcon(urls)
            oms.open_falcon()
    f.close()
    writemysql()
    result()
    alarm()
    alarm_ok()
    alarm_class()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
