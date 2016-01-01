#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  
#coding:utf-8

#sys.setdefaultencoding('utf-8')

debug = False
#debug = True
if __name__ == '__main__':
    debug = True
else:
    debug = False

import platform
import sys, os
 
user = 'root'
pwd  = '654321'
host = '127.0.0.1'
db   = 'sat'

cnx = None
cursor = None
errMysql = None

localplatform = platform.platform()
if localplatform[:5] == 'Linux': #为了windown os 不存在mysql情况
    import mysql   
    import mysql.connector

    cnx = mysql.connector.connect(user=user, password=pwd, host=host, database=db, charset='utf8')
    cursor = cnx.cursor()
    errMysql = mysql.connector.Error

def ConClose():
    if cnx != None and cursor != None:
        cursor.close()
        cnx.close()

def Insert(inHead, ldata):
    try:
        if cursor != None:
            cursor.execute(inHead, ldata)
            cursor.execute('commit')
    except errMysql:
        print(inHead)
        print("Error: {}".format(errMysql.msg))

def Select(cmd):
    try:
        if cursor != None:
            cursor.execute(cmd)
    except errMysql:
        print(cmd)
        print("Error: {}".format(errMysql.msg))


    
if __name__ == '__main__':
    print('test mysql connect', cnx, cursor)
    ConClose()
"""
in_price = "insert into t_price(code,tradedate,OpeningPrice,Transactionprice,HighestPrice,LowestPrice,Bidprice,Offerprice,Closingprice,Changes,PriceChange,Volumes,Turnover,TotalMarket,Items,EscrowShares,CirculationShares,Indate,F001,F002,F003,F004,F007,F008) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

insert_sql = "INSERT INTO t_stock_code(code, name, indate) VALUES ('000002.SZ', '万科A', '2014-11-30')"
select_sql = "SELECT * FROM t_stock"

try:
    cursor.execute(in_price,(value1,value2,value3))
    cursor.execute(select_sql)
    data = cursor.fetchall()
    for i in data:
        print(i)
except mysql.connector.Error as err:
    print("create table 'mytable' failed.")
    print("Error: {}".format(err.msg))
    sys.exit()
 
try:
    cursor.execute(insert_sql)
except mysql.connector.Error as err:
    print("insert table 't_stock_code' failed.")
    print("Error: {}".format(err.msg))
    sys.exit()

if os.path.exists(data_file):
    myfile = open(data_file)
    lines = myfile.readlines()
    myfile.close()
 
    for line in lines:
        myset = line.split()
        sql = "INSERT INTO t_stock_code (id, code, name) VALUES ('{}', {}, {})".format(myset[0], myset[1], myset[2])
        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            print("insert table 't_stock_code' from file 'mysql-test.dat' -- failed.")
            print("Error: {}".format(err.msg))
            sys.exit()

try:
    cursor.execute(select_sql)
    for (id, code, name) in cursor:
        print("id:{}  code:{}  name:{}".format(id, code, name))
except mysql.connector.Error as err:
    print("query table 't_stock_code' failed.")
    print("Error: {}".format(err.msg))
    sys.exit()
"""
 
