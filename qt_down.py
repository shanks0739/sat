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
import time
import random
import urllib
import urllib.request

import sat_util
import sat_down

#debug=False
debug = True

if __name__ == '__main__':
    debug = True
else:
    debug = False

PriceDataLen = 50

def FillSingleDict(slist):
    qtDict={}
    bRet = False
    if (len(slist) >= PriceDataLen):
        #print(len(slist))
        #只是返回一个字典
        qtDict['locate'] = slist[0] # 代码代号 sz,sh
        qtDict['name'] = slist[1] # 代码名字
        qtDict['code'] = slist[2] # 代码，应该不需要包含sz,sh,hk
        qtDict['cur'] = (slist[3])     # 当前价格
        qtDict['closed'] = (slist[4]) #昨天收盘价
        qtDict['opening'] = (slist[5]) #开盘价
        qtDict['outdisk'] = (slist[7])
        qtDict['indisk'] = (slist[8]) 
        qtDict['buy1'] = (slist[9])
        qtDict['buy1volume'] = (slist[10])
        qtDict['buy2'] = (slist[11])
        qtDict['buy2volume'] = (slist[12])
        qtDict['buy3'] = (slist[13])
        qtDict['buy3volume'] = (slist[14])
        qtDict['buy4'] = (slist[15])
        qtDict['buy4volume'] = (slist[16])
        qtDict['buy5'] = (slist[17])
        qtDict['buy5volume'] =(slist[18])
        qtDict['sell1'] = (slist[19])
        qtDict['sell1volume'] = (slist[20])
        qtDict['sell2'] = (slist[21])
        qtDict['sell2volume'] =(slist[22])
        qtDict['sell3'] = (slist[23])
        qtDict['sell3volume'] = (slist[24])
        qtDict['sell4'] = (slist[25])
        qtDict['sell4volume'] =(slist[26])
        qtDict['sell5'] = (slist[27])
        qtDict['sell5volume'] =(slist[28])
        qtDict['date'] = slist[30][:8] # date
        qtDict['time'] = slist[30][8:] #time
        qtDict['updown'] = (slist[31]) #涨跌  
        qtDict['updownrate'] = (slist[32]) #涨跌幅% 
        qtDict['highest'] = (slist[33])
        qtDict['lowest'] = (slist[34])
        qtDict['volume'] = (slist[36]) #总成交量
        qtDict['turnover'] = (slist[37]) #总成交额（万）
        qtDict['turnoverrate'] = (slist[38]) #换手率
        qtDict['earningsrate'] = slist[39]
        qtDict['amplitude'] = (slist[43])
        qtDict['pb'] = (slist[46])
        qtDict['uplimit'] = (slist[47])
        qtDict['downlimit'] = (slist[48])
        bRet = True
        if (debug): print(slist[30], '  ', qtDict['date'], '  ', qtDict['time'])
    return bRet, qtDict
 
#这个函数需要做成多态的形式，不同的来源，格式是不一样的。
def QtParseSingle(s):  
    if(debug): print('QtParseSingle', type(s))  
    #slist=s[12:] #此处应该使用更好的方式 
    #if(debug): print(slist)  
    #slist=slist.split('~')
    
    slist=s.split('~')
    slist[0] = slist[0][2:4]
    return FillSingleDict(slist)
   
    

#所有的code，应该是不带有参数的，应该由各自转化为相应的合适完整请求代码  
qurl='http://qt.gtimg.cn/'              
def QtDown(code):
    code=sat_util.codeAddPrefix(code)
    durl=qurl+'r='+str(random.random())+'&q='+code
    #durl=qurl+code
    if (debug): print(durl)
    s = sat_down.GetRtPriceByURL(durl)
    if s == '':
        return False,None
    strGB=sat_util.ToGB(s)
    return QtParseSingle(strGB)


# 多个代码一起调用
def QtParseMulti(s):  
    if(debug): print(type(str))
    ldict=[]
    if s == None:
        return ldict
    for l in s:
        if (debug): print(l)
        #l = str(l)
        strGB=sat_util.ToGB(l)
        b, d=QtParseSingle(strGB)
        if b:
            ldict.append(d)
    return ldict


def QtDownMulti(codes):
    qcode=''
    for i in range(0, len(codes)):
        qcode += sat_util.codeAddPrefix(codes[i]) +','
    durl=qurl+'r='+str(random.random())+'&q='+qcode
    if (debug): print(durl)
    s=sat_down.GetMultiRtPriceByURL(durl)
    if (debug): print(s, len(s))
    return QtParseMulti(s)

def Test():
    codes=sat_util.GetAllCodesFromCSV()
    qcodes=codes[0:3]
    ldict=QtDownMulti(qcodes)
    for i in range(0, len(ldict)):
        print(ldict[i])
    b,d=QtDown(codes[0])
    print(b, d)

if __name__ == '__main__':
    start = time.time()
    Test()
    end = time.time()
    print("qt down s %d" %(end - start))
