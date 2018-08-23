#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import MySQLdb
class op_mysql:
    def mysql_command(self,sql_cmd):
        try:
            ret =[]
            conn = MySQLdb.connect('localhost','root','mysql@2016','system_openfalcon',charset='utf8')
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            conn.commit()
            for row in cursor.fetchall():
                for i in row:
                    # print i
                    ret.append(row)
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        return ret

    def mysql_create(self, create_table):
        try:
            ret = []
            conn = MySQLdb.connect('localhost', 'root', 'mysql@2016', 'system_openfalcon', charset="utf8")
            cursor = conn.cursor()
            cursor.execute(create_table)
            conn.commit()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        return ret

    def select_count_table(self, sql_cmd):
        try:
            ret = []
            conn = MySQLdb.connect('localhost', 'root', 'mysql@2016', 'system_openfalcon', charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            # 使用cur.rowcount获取结果集的条数
            numrows = int(cursor.rowcount)
            # 循环numrows次，每次取出一行数据
            for i in range(numrows):
                # 每次取出一行，放到row中，这是一个元组(id,name)
                row = cursor.fetchone()
                # 直接输出两个元素
                datas = row[0], row[1],row[2],row[3], row[4],row[5],row[6]
                ret.append(datas)
        except MySQLdb.Error, e:
            ret.append(e)
        return ret

    def select_room_table(self, sql_cmd):
        try:
            ret = []
            conn = MySQLdb.connect('localhost', 'root', 'mysql@2016', 'system_openfalcon', charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            numrows = int(cursor.rowcount)
            # 循环numrows次，每次取出一行数据
            for i in range(numrows):
                # 每次取出一行，放到row中，这是一个元组(id,name)
                row = cursor.fetchone()
                # 直接输出两个元素
                datas = row[0]
                ret.append(datas)
        except MySQLdb.Error, e:
            ret.append(e)
        return ret

    def select_ip_row1(self, sql_cmd):
        try:
            ret = []
            conn = MySQLdb.connect('localhost', 'root', 'mysql@2016', 'system_openfalcon', charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            numrows = int(cursor.rowcount)
            # 循环numrows次，每次取出一行数据
            for i in range(numrows):
                # 每次取出一行，放到row中，这是一个元组(id,name)
                row = cursor.fetchone()
                # 直接输出两个元素
                datas = row[0], row[1]
                ret.append(datas)
        except MySQLdb.Error, e:
            ret.append(e)
        return ret
