#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

"""
这个文件是一个下载接口， 
"""

import urllib  
import urllib.request
import time
import datetime


"""
global var
"""

debug = False
#debug = True
if __name__ == '__main__':
    debug = True
else:
    debug = False

"""
公共下载接口
"""
import qt_down
import sn_down
import yh_down

def Down(code):
    return qt_down.QtDown(code)

def DownMulti(codes):
    return qt_down.QtDownMulti(codes)

def DownHistorySN(code, dtEnd, dtStart, f):
    sn_down.SinaDownHistory(code, dtEnd, dtStart, f)

def DownHistoryYH(code, dtEnd, dtStart, f):
    yh_down.YahooDownHistory(code, dtEnd, dtStart, f)
    
"""
获取实时数据，这个可以优化文件句柄
不是每一个链接都创建一个文件句柄，可以使用文件句柄池，不用每次都打开
"""
def GetRtPriceByURL(url):
    try:
        f= urllib.request.urlopen(url)  
        if(debug): print(f.geturl())  
        if(debug): print(f.info())  
        return f.readline()
        f.close()
    except IOError:
        print("url open failed", url)
        return ''

#最好的方式是调用方控制readlines()的大小，保证一次就能返回所有的数据。
#如果超出大小，该函数会提示错误，程序退出
def GetMultiRtPriceByURL(url):
    try:
        f= urllib.request.urlopen(url)  
        if(debug): print(f.geturl())  
        if(debug): print(f.info())  
        return f.readlines()
        f.close()
    except IOError:
        print("url open failed ....", url)
        return None


def Test():
    codes = ['sh601398']
    url = 'http://qt.gtimg.cn/q='+codes[0]
    print(GetRtPriceByURL(url))

def TeestMulti():
    codes=['000001','000002']
    print(DownMulti(codes))

    
if __name__ == '__main__':
    start = time.time()
    Test()
    #TestMulti()
    end = time.time()
    print("url open second %d" %(end - start))

