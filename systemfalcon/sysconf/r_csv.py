import pandas
import MySQLdb


def load_csv():
    f_path = '/systemfalcon/systemfalcon/static/sysconf/'
    d = pandas.read_excel(f_path+'CDN_info.xlsx','Sheet1',index_col=None)
    d.to_csv(f_path+'zdl.csv',encoding='utf-8')
    with open(f_path+'zdl.csv','r') as f:
        with open(f_path+'zdl2.csv','w') as f2:
            f2.truncate()
            for i in f.readlines():
                a = i.split(',', 8)[0]
                if a == '':
                    b = 1
                else:
                    b = int(a)+2
                id = str(b)
                p1 = i.split(',', 8)[1]
                p2 = i.split(',', 8)[2]
                p3 = i.split(',', 8)[3]
                p4 = i.split(',', 8)[4]
                p5 = i.split(',', 8)[5]
                p6 = i.split(',', 8)[6]
                p7 = i.split(',', 8)[7]

                s = id+','+p1+','+p2+','+p3+','+p4+','+p5+','+p6+','+p7
                s.replace(',,',',None,').replace(',,',',None,')
                f2.write(s + '\n\n')

    sql_load1 = """truncate sysconf_room_bandwidth ;"""
    sql_load2 = """load data local infile '/systemfalcon/systemfalcon/static/sysconf/zdl2.csv' 
    into table sysconf_room_bandwidth fields terminated by ',' enclosed by '"' lines terminated by '\\n\\n';"""
    conn2 = MySQLdb.connect('127.0.0.1', 'root', 'mysql@2016', 'system_openfalcon')
    cur2 = conn2.cursor()
    cur2.execute(sql_load1)
    cur2.execute(sql_load2)
    conn2.close()
