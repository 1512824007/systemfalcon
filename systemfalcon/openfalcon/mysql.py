#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pymysql

class db_operate:
    def mysql_command(self,sql_cmd):
        ret = []
        try:
            conn=pymysql.connect('127.0.0.1','root','mysql@2016','openfalcon',charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            conn.commit()
            for row in cursor.fetchall():
                # for i in row:
                ret.append(row)
        except pymysql.Error as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))

        return ret
        # return ret

    def select_table(self,sql_cmd):
        ret = []
        try:
            conn = pymysql.connect('127.0.0.1', 'root', 'mysql@2016', 'openfalcon', charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            conn.commit()
            for row in cursor.fetchall():
                for i in row:
                    ret.append(i)
        except pymysql.Error as e:
            ret.append(e)
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return ret
        # return ret
    def select_count_table(self,sql_cmd):
        ret = []
        try:
            conn=pymysql.connect('127.0.0.1','root','mysql@2016','openfalcon',charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            # 使用cur.rowcount获取结果集的条数
            numrows = int(cursor.rowcount)

            # 循环numrows次，每次取出一行数据
            for i in range(numrows):
                # 每次取出一行，放到row中，这是一个元组(id,name)
                row = cursor.fetchone()
                # 直接输出两个元素

                datas = row[0]

                ret.append(datas)
        except pymysql.Error as e:
            ret.append(e)
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return ret


