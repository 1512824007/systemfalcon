#!/usr/bin/env python
#-*- coding:utf-8 -*-
import MySQLdb
import config

class db_operate:
    def mysql_command(self,sql_cmd):
        ret = []
        try:
            conn = MySQLdb.connect('{0}'.format(config.DASHBOARD_DB_HOST), 'root', '123321', 'graph')
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            conn.commit()
            ret = cursor.fetchall()
        except MySQLdb.Error as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))

        return ret





