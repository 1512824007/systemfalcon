# -*- coding: utf-8 -*-
import mysql_graph
from top10.scrpits import rrdgraph
from collections import Counter
import json
import os
import time

db_graph = mysql_graph.db_operate()


class m_angle_band():

    def __init__(self):
        pass

    def room_speed(self, room):

        sql_host_graph = "select distinct endpoint from endpoint;"
        h = db_graph.mysql_command(sql_host_graph)

        try:
            speed = 22000 
            return speed
        except Exception as e:
            print e

    def host_speed(self, host):
        try:
            speed = 1200
            return speed
        except Exception as e:
            print e

    def pro_speed(self, pro):
        pass

    def grp_speed(self, grp):
        pass


class all_c():

    def __init__(self):
        pass

    def room_pro_t(self, counter, room, pro, start=int(time.time())-42600, end=int(time.time())-60):
        sql_all = "select a.hostname, b.name, b.abbr_name, c.name, c.abbr_name, e.name, e.abbr_name \
        from device_server as a, business_project as b, business_cluster as c, business_clusterserver as d, idc_idc as e \
        where a.id = d.device_id and b.id = c.project_id and c.id = d.cluster_id  and e.id= a.idc_id;"
        h = [['a.hostname', 'b.name', 'b.abbr_name', 'c.name', 'c.abbr_name', 'e.name', 'e.abbr_name']]
        a = {}
        dict_count = Counter(a)
        for i in h:
            flow_counters = [counter]
            endpoint_counters = [i[0]]

            query_result = rrdgraph.graph_query(endpoint_counters,flow_counters, start=start, end=end)
            for j in range(0, len(query_result)):
                x = query_result[j]
                try:
                    if x["Values"] != None:
                        xv = []
                        for v in x['Values']:
                            if v["value"] == None:
                                s = [v["timestamp"] * 1000.0, 0]
                            else:
                                s = [v["timestamp"] * 1000.0, v["value"]]
                            xv.append(s)
                        dict_count += Counter(dict(xv))
                except:
                    pass
        data = list(sorted(dict_count.items()))

        GD = json.dumps(data)

        f1 = '/systemfalcon/systemfalcon/static/top10/{0}/{1}/{2}/room_service'.format(counter, room, pro)
        f2 = '/systemfalcon/systemfalcon/static/top10/{0}/{1}/{2}/room_service_max_min'.format(counter, room, pro)
        dir1 = '/systemfalcon/systemfalcon/static/top10//{0}/{1}/{2}/'.format(counter, room, pro)
        if not os.path.exists(f1):
            if not os.path.exists(dir1):
                os.makedirs(dir1)
            os.system('touch ' + f1)
            os.system('touch ' + f2)

        f = open(f1, 'w')
        f.write(GD)
        f.close()
        try:
            max_data = max(dict_count.values())
            min_data = min(dict_count.values())
            a = open(f2, 'w')
            a.write(str(max_data) + ' ' + str(min_data))
            a.close()
        except Exception as e:
            print e
