#!/usr/bin/env python3  
#coding=utf-8
# -*- coding:utf-8 -*-  

debug = False
#debug = True

import time
import redis

#redis db1 , save realtime price data
r =  redis.StrictRedis(host='localhost', port=6379, db=1)

#r=redis.Redis(host='localhost', port=6379, db=0)
#import redisco #import models  

#redis db0 , save history price data
rh = redis.StrictRedis(host='localhost', port=6379, db=0)
#why select db0 as history datebase, because mysql,csv script program operate default datebase and db0 is default datebase

def TestRedisInfo():
    info = r.info()
    for key in info:
        print("%s: %s" %(key, info[key]))
    print("\ndbsize: %s"%r.dbsize())
    print("ping %s" %r.ping())

def TestReidsHistory():
    info = rh.info()
    for key in info:
        print("%s: %s" %(key, info[key]))
    print("\ndbsize: %s"%rh.dbsize())
    print("ping %s" %rh.ping())

if __name__ == '__main__':
    start = time.time()
    TestReidsHistory()
#    TestRedisInfo()
#    print('redis ', r.ping())
#    r['test'] = 'test' #或者可以r.set(‘test’, ‘test’) 设置key
#    print(r.get('test'))  #获取test的值
#    print(r.delete('test')) #删除这个key
#    print(r.flushdb()) #清空数据库
#    print(r.keys()) #列出所有key
#    print(r.exists('test')) #检测这个key是否存在
#    print(r.dbsize()) #数据库中多少个条数
#    print('reids ', r.ping())
    end = time.time()
    print("ms %d" %(end - start))
