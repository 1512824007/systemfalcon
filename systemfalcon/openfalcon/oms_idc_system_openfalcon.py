#!/usr/bin/env python
#-*- coding:utf-8 -*-


import mysql_oms,mysql_systemfalcon

db_oms = mysql_oms.db_operate()
db_systemopenfalcon = mysql_systemfalcon.db_operate()


def oms_systemopenfalcon():
    try:
        delete = "delete from openfalcon_roomname;"
        db_systemopenfalcon.mysql_command(delete)
        sql = "select id,ext_info,created_time,name,abbr_name,country,province,city,address,phone,email,room_number from idc_idc;"
        row = db_oms.mysql_command(sql)
        for result_oms in row:
            sql1 = "insert into openfalcon_roomname(id,ext_info,created_time,name,abbr_name,country,province,city,address,phone,email,room_number)" \
                   " VALUE('%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');"%(result_oms[0],result_oms[1],result_oms[2],result_oms[3],result_oms[4],result_oms[5],result_oms[6],result_oms[7],result_oms[8],result_oms[9],result_oms[10],result_oms[11])
            db_systemopenfalcon.mysql_command(sql1)
        print('OK')
    except Exception as e:
        print(e)
        pass
