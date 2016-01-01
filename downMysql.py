#!/usr/bin/env python3  
#coding=utf-8
# -*- coding:utf-8 -*-  


"""
golbal var
"""  
debug = False
#debug = True

from sys import path
path.append(r"../")

import time
import sat_dbop


if __name__ == '__main__':
    start = time.time()
    sat_dbop.WName2Redis()
    #Plate2Redis()
    #WAll2MysqlOnce()
    #WAll2RedisOnce()
    #WAll2RedisByTime()
    #TestRedisRead()
    #WAll2CSVHistory()
    #WAll2CSVHistoryOnce()
    #W2RedisByCSV()
    #TestDelKeys()
    #TestWAlgoParams()
    #TestRAlgoParams()
    #TestRAllAlgoParams()
    end = time.time()
    print("total s %d" %(end - start))
