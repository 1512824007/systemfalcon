#!/usr/bin/env python
#-*- coding:utf-8 -*-
import MySQLdb
from top10 import config


class db_operate:
    def __init__(self):
        self.conn = MySQLdb.connect('{0}'.format(config.DASHBOARD_DB_HOST),'root','xiaoheshang2926','falcon_portal',charset="utf8")
    def mysql_command(self,sql_cmd):
        ret = []
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
            self.conn.commit()
            for row in cursor.fetchall():
                # for i in row:
                ret.append(row)
            self.conn.close()
        except MySQLdb.Error as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))

        return ret


    def select_table(self,sql_cmd):
        ret = []
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
            self.conn.commit()
            for row in cursor.fetchall():
                for i in row:
                    ret.append(i)
        except MySQLdb.Error as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
            ret.append(e)
        return ret
        # return ret
    def select_count_table(self,sql_cmd):
        ret = []
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_cmd)
            # 使用cur.rowcount获取结果集的条数
            numrows = int(cursor.rowcount)

            # 循环numrows次，每次取出一行数据
            for i in range(numrows):
                # 每次取出一行，放到row中，这是一个元组(id,name)
                row = cursor.fetchone()
                # 直接输出两个元素
                datas = row[0],row[1]
                ret.append(datas)
            self.conn.close()
        except MySQLdb.Error as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
            ret.append(e)
        return ret

    def call_proc(self,src_ip,dest_ip,start_time,end_time):
        try:
            cursor = self.conn.cursor()
            cursor.execute('call net_flow_report(%s,%s,%s,%s)',(src_ip,dest_ip,start_time,end_time))
            self.conn.commit()
            for row in cursor.fetchall():
                print(row)
            self.conn.close()
        except MySQLdb.Error as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
            print(e)

    def call_proc_update(self, src_ip, dest_ip, start_time, end_time):
        try:
            cursor = self.conn.cursor()
            cursor.execute('call net_flow_report_update(%s,%s,%s,%s)', (src_ip, dest_ip, start_time, end_time))
            self.conn.commit()
            for row in cursor.fetchall():
                print(row)
            self.conn.close()
        except MySQLdb.Error as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))