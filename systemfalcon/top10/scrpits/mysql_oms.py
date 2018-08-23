#!/usr/bin/env python
#-*- coding:utf-8 -*-
import MySQLdb

class db_operate:
    def mysql_command(self,sql_cmd):
        try:
            ret = []
            conn=MySQLdb.connect('127.0.0.1','root','mysql@2016','beacon',charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            conn.commit()
            for row in cursor.fetchall():
                # for i in row:
                ret.append(row)
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

        return ret
        # return ret

    def select_table(self,sql_cmd):
        try:
            ret = []
            conn = MySQLdb.connect('127.0.0.1', 'root', 'mysql@2016', 'beacon', charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            conn.commit()
            for row in cursor.fetchall():
                for i in row:
                    ret.append(i)
        except MySQLdb.Error,e:
            ret.append(e)
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        return ret
        # return ret
    def select_count_table(self,sql_cmd):
        try:
            ret = []
            conn=MySQLdb.connect('127.0.0.1','root','mysql@2016','beacon',charset="utf8")
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            # 使用cur.rowcount获取结果集的条数
            numrows = int(cursor.rowcount)

            # 循环numrows次，每次取出一行数据
            for i in range(numrows):
                # 每次取出一行，放到row中，这是一个元组(id,name)
                row = cursor.fetchone()
                # 直接输出两个元素
                datas = row[0],row[1],row[2],row[3],row[4],row[5]
                ret.append(datas)
        except MySQLdb.Error,e:
            ret.append(e)
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        return ret
# if __name__ == "__main__":
#     ms = db_operate()
#     print ms.mysql_command(sql_cmd='select idc_name from res_idc_bak;')
#     data =  ms.select_table('select idc_name from res_idc_bak')
#
#     for row in data:
#         print row

