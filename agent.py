#!/bin/python

import pymysql
import datetime

with open ("/run/secrets/mysql_userr", "r") as secrets:
    user = secrets.readline().replace("\n","")

with open ("/run/secrets/mysql_rpass", "r") as secrets:
    password = secrets.readline().replace("\n","")

def convert2str(record):
    res = []
    for item in record:
        if item == None:
            res.append('NULL')
        elif type(item) == str:
            res.append('"' + item.replace('"', '\\"') + '"')
        elif type(item) == datetime.datetime:
            res.append('"' + str(item) + '"')
        else:  # for numeric values
            res.append(str(item))
    return ','.join(res)

def copy_table(src_name, src_cursor, dst_name, dst_cursor):
    sql = 'select * from %s'%src_name
    src_cursor.execute(sql)
    res = src_cursor.fetchall()
    cnt = 0
    for record in res:
        val_str = convert2str(record)
        try:
            sql = 'insert into %s values(%s)'%(dst_name, val_str)
            dst_cursor.execute(sql)
            cnt += 1
        except Exception as e:
            print(sql, e)
    return cnt

def update_time(dst_cursor):

    now=datetime.datetime.now()
    sql = 'update healthcheck set reg_date="%s" WHERE service="webapp"'%(now)
    try:
        dst_cursor.execute(sql)

    except Exception as e:
            print(sql, e)


def main():

    mysql = pymysql.connect(host="db", user=user, passwd=password, db="appBD", port=3306)
    mysql1 = pymysql.connect(host="db", user=user, passwd=password, db="information_schema", port=3306)
    mysql2 = pymysql.connect(host="db", user=user, passwd=password, db="nextcloud", port=3306)

    #create cursor
    dst_cur = mysql.cursor()
    src_cur1 = mysql1.cursor()
    src_cur2 = mysql2.cursor()
:q
    #delete records and regenerate tables
    delete1 = dst_cur.execute("TRUNCATE TABLE app_activity")
    delete2 = dst_cur.execute("TRUNCATE TABLE app_users")
    delete3 = dst_cur.execute("TRUNCATE TABLE app_authtoken")
    delete4 = dst_cur.execute("TRUNCATE TABLE app_status")

    copy_table("oc_activity", src_cur2,"app_activity", dst_cur)
    copy_table("oc_users", src_cur2 , "app_users", dst_cur)
    copy_table("oc_authtoken", src_cur2, "app_authtoken", dst_cur)
    copy_table("GLOBAL_STATUS", src_cur1, "app_status", dst_cur)
    update_time(dst_cur)

    mysql.commit()

    dst_cur.close()
    src_cur1.close()
    src_cur2.close()

    print "update_done"

if __name__ =='__main__':
    main()
