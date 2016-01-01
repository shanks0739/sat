#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

"""
http://www.2cto.com/kf/201212/178371.html
download data from qq.
http://qt.gtimg.cn/q=sz000858
以 ~ 分割字符串中内容，下标从0开始，依次为
[html] 
 0: 未知  1: 名字  2: 代码  3: 当前价格  4: 昨收  5: 今开  6: 成交量（手）  
 7: 外盘  8: 内盘  9: 买一  10: 买一量（手）  11-18: 买二 买五  
 19: 卖一  20: 卖一量  21-28: 卖二 卖五  29: 最近逐笔成交  30: 时间  
 31: 涨跌  32: 涨跌%  33: 最高  34: 最低  35: 价格/成交量（手）/成交额  
 36: 成交量（手）  37: 成交额（万）  38: 换手率  39: 市盈率  40:   
 41: 最高  42: 最低  43: 振幅  44: 流通市值  45: 总市值  46: 市净率  
 47: 涨停价  48: 跌停价  
"""

"""
use redis save real-time price, key/values(is list, insert(0,RealTimePrice))
focus,not focus, 

sat_algo.py file is 
"""   

import urllib  
import urllib.request
import time
import datetime

"""
sat py
"""
import sat_rtprice

dt = datetime.datetime.now()
  

#debug=True  
debug=False  
      
import sat_down

def SaveRealtimeToList(rp):
    lrp.insert(0, rp)
    if (debug):
        for i in range(0,len(lrp)):
            lrp[i].PricePrint()


import threading
import datetime
import sat_thread

  
#main thread sat start here
def main():
    """
    这个地方应该是获取需要关注的股票代码，并且不同代码对应一个线程定时获取，获取的数据保存起来，
    """
    #先做定时获取，然后对不同代码进行线程化。
    #暂时从文件中获取所有股票，
    #GetAllCodeFromCSV()
    #经过算法得出关注的代码，然后实时查看数据，如果达到预期就应该提示。
    #这些代码是算法前一天运行得出的结果，或者人工添加的代码。
    focuscode = ['sh601398','sh601818']#, 'sh601818'
    if (len(focuscode) == 0):
        print("focuscode empty")
        return False
#
#    nloops=range(len(focuscode))
#    for i in nloops:
#        t=SAT_ThreadClass(SAT_EvalByCode, focuscode[i], focuscode[i])
#        threads.insert(0, t)
#
#    nloops=range(len(threads))
#    print(nloops)
#    for i in nloops:
#        threads[i].start()
#        #time.sleep(1)
#    for i in nloops:
#        threads[i].join()
#              
#    for i in range(0,len(lrp)):
#        lrp[i].PricePrint()
#        
#        

 
  


if __name__ == '__main__':
    start = time.time()
    end = time.time()
    print("ms %d" %(end - start))
