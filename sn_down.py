#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

"""
sina 每5秒刷一次数据
download data from sina.
查询大盘指数，比如查询上证综合指数（000001）：
http://hq.sinajs.cn/list=s_sh000001

http://hq.sinajs.cn/list=sh600586,sh600004
以 , 分割字符串中内容，下标从0开始，依次为
[html] 
0：”大秦铁路”，股票名字；
1：”27.55″，今日开盘价；
2：”27.25″，昨日收盘价；
3：”26.91″，当前价格；
4：”27.55″，今日最高价；
5：”26.20″，今日最低价；
6：”26.91″，竞买价，即“买一”报价；
7：”26.92″，竞卖价，即“卖一”报价；
8：”22114263″，成交的股票数，由于股票交易以一百股为基本单位，所以在使用时，通常把该值除以一百；
9：”589824680″，成交金额，单位为“元”，为了一目了然，通常以“万元”为成交金额的单位，所以通常把该值除以一万；
10：”4695″，“买一”申请4695股，即47手；
11：”26.91″，“买一”报价；
12：”57590″，“买二”
13：”26.90″，“买二”
14：”14700″，“买三”
15：”26.89″，“买三”
16：”14300″，“买四”
17：”26.88″，“买四”
18：”15100″，“买五”
19：”26.87″，“买五”
20：”3100″，“卖一”申报3100股，即31手；
21：”26.92″，“卖一”报价
(22, 23), (24, 25), (26,27), (28, 29)分别为“卖二”至“卖四的情况”
30：”2008-01-11″，日期；
31：”15:05:32″，时间；
"""
import time
import datetime
import random
import urllib
import urllib.request

import sat_util
import sat_down

debug=False
#debug = True


PriceDataLen = 31

def FillSingleDict(slist):
    sinaDict={}
    bRet = False
    if (len(slist) >= PriceDataLen):
        #print(len(slist))
        #只是返回一个字典
        sinaDict['opening'] = (slist[1]) #开盘价 
        sinaDict['closed'] = (slist[2]) #昨天收盘价
        sinaDict['cur'] = (slist[3])     # 当前价格
        sinaDict['highest'] = (slist[4])
        sinaDict['lowest'] = (slist[5])
        sinaDict['buy1'] = (slist[6])
        sinaDict['sell1'] = (slist[7])
        sinaDict['volume'] = (slist[8]) #总成交量
        sinaDict['turnover'] = (slist[9]) #总成交额（万）        
        sinaDict['buy1volume'] = (slist[10])
        #sinaDict['buy1'] = (slist[11])
        sinaDict['buy2volume'] = (slist[12])
        sinaDict['buy2'] = (slist[13])
        sinaDict['buy3volume'] = (slist[14])
        sinaDict['buy3'] = (slist[15])
        sinaDict['buy4volume'] = (slist[16])
        sinaDict['buy4'] = (slist[17])
        sinaDict['buy5volume'] =(slist[18])
        sinaDict['buy5'] = (slist[19])
        sinaDict['sell1volume'] = (slist[20])
        #sinaDict['sell1'] = (slist[21])
        sinaDict['sell2volume'] = (slist[22])
        sinaDict['sell2'] = (slist[23])
        sinaDict['sell3volume'] = (slist[24])
        sinaDict['sell3'] = (slist[25])
        sinaDict['sell4volume'] = (slist[26])
        sinaDict['sell4'] = (slist[27])
        sinaDict['sell5volume'] =(slist[28])
        sinaDict['sell5'] = (slist[29])
        sinaDict['date'] = slist[30] # date
        sinaDict['time'] = slist[31] #time
        sinaDict['code'] = slist[33] # 代码，应该不需要包含sz,sh,hk
        #下面是自己算的
        cur = float(slist[3])
        opening = float(slist[1])
        sinaDict['updown'] =  cur - opening#涨跌
        if (opening > 0.01):
            sinaDict['updownrate'] = (cur - opening) / opening #涨跌幅%
        else:
            sinaDict['updownrate'] = 0
        sinaDict['uplimit'] = opening * 1.1 #最高10%
        sinaDict['downlimit'] = opening * 0.9 #最低10%
        
        sinaDict['turnoverrate'] = 0 #换手率
        sinaDict['earningsrate'] = 0
        sinaDict['amplitude'] = 0
        sinaDict['pb'] = 0
        sinaDict['outdisk'] = 0
        sinaDict['indisk'] = 0
        
        bRet = True
        if (debug): print(slist[30], '  ', sinaDict['date'], '  ', sinaDict['time'])
    return bRet, sinaDict
 
#这个函数需要做成多态的形式，不同的来源，格式是不一样的。
def SinaParseSingle(s):  
    if(debug): print('SinaParseSingle', type(s))  
    slist=s[13:] #此处应该使用更好的方式
    code=slist[:6]
    if(debug): print(slist, code)  
    slist=slist.split(',')
    slist.append(code)
    if (debug): print(slist)
    return FillSingleDict(slist)
   
    

#所有的code，应该是不带有参数的，应该由各自转化为相应的合适完整请求代码  
qurl='http://hq.sinajs.cn/'
qcodePrefix='&list='
qrandomPrefix='r='
def SinaDown(code):
    code=sat_util.codeAddPrefix(code)
    durl=qurl+qrandomPrefix+str(random.random())+qcodePrefix+code
    if (debug): print(durl)
    s = sat_down.GetRtPriceByURL(durl)
    if s == '':
        return False,None
    strGB=sat_util.ToGB(s)
    return SinaParseSingle(strGB)


# 多个代码一起调用
def SinaParseMulti(s):  
    if(debug): print(type(str))
    ldict=[]
    for l in s:
        if (debug): print(l)
        strGB=sat_util.ToGB(l)
        b, d=SinaParseSingle(strGB)
        if b:
            ldict.append(d)
    return ldict


def SinaDownMulti(codes):
    qcode=''
    for i in range(0, len(codes)):
        qcode += sat_util.codeAddPrefix(codes[i]) +','
    durl=qurl+qrandomPrefix+str(random.random())+qcodePrefix+qcode
    if (debug): print(durl)
    s=sat_down.GetMultiRtPriceByURL(durl)
    if (debug): print(s, len(s))
    return SinaParseMulti(s)

def Test():
    codes=sat_util.GetAllCodesFromCSV()
    qcodes=codes[0:3]
    ldict=SinaDownMulti(qcodes)
    for i in range(0, len(ldict)):
        print(ldict[i])
    #b,d=SinaDown(codes[0])
    #print(b, d)

#这个链接只能得到2000年后的历史数据
qurlHis='http://biz.finance.sina.com.cn/stock/flash_hq/kline_data.php?'
qcodePre='&symbol='
qrandomPre='&rand='
qdtEndPre='&end_date='
qdtStartPre='&begin_date='
qtype='&type=plain'
"""
        ldict={}
        ldict['code']=code[2:]
        ldict['date']=slist[0]
        ldict['opening'] = slist[1] 
        ldict['highest'] = slist[2]
        ldict['cur'] = slist[3]
        ldict['lowest'] = slist[4]
        ldict['volume'] = slist[5]
"""
#Date	Open	High Close(cur) Low Volume	
def SinaDownHistory(code, dtEnd, dtStart, f):
    qcode=sat_util.codeAddPrefix(code)
    insCode=qcode[2:]
   
    yEnd = int(dtEnd.year)
    mEnd = int(dtEnd.month)
    dEnd = int(dtEnd.day)
    yStart=int(dtStart.year)
    mStart = int(dtStart.month)
    dStart = int(dtStart.day) 

    qyEnd = ''
    qmEnd = ''
    qdEnd = ''
    qyStart = ''
    qmStart = ''
    qdStart = ''
    
    for i in range(yStart, yEnd+1):
        if i == yEnd and i == yStart:
            qmEnd = str(mEnd)
            qdEnd = str(dEnd)
            qmStart = str(mStart)
            qdStart = str(dStart)
        elif i == yEnd and i > yStart:
            qmEnd = str(mEnd)
            qdEnd = str(dEnd)
            qmStart = '01'
            qdStart = '01'              
        elif i < yEnd and i > yStart:
            qmEnd = '12'
            qdEnd = '31'
            qmStart = '01'
            qdStart = '01'       

        elif i < yEnd and i == yStart:
            qmEnd = '12'
            qdEnd = '31'
            qmStart = str(mStart)
            qdStart = str(dStart)
        else:
            print("date error, give up this query")
            break
        
        qyEnd = str(i)
        qyStart = qyEnd
        if len(qmEnd) < 2:
            qmEnd = '0'+qmEnd
        if len(qdEnd) < 2:
            qdEnd = '0' + qdEnd
        if len(qmStart) < 2:
            qmStart = '0'+qmStart
        if len(qdStart) < 2:
            qdStart = '0' + qdStart
        
        qDate = qdtEndPre+qyEnd+qmEnd+qdEnd+qdtStartPre+qyStart+qmStart+qdStart
        durl=qurlHis+qrandomPre+str(random.randint(0,10000))+qcodePre+qcode+qDate+qtype
        if (debug): print(durl)
        s = sat_down.GetMultiRtPriceByURL(durl)
        if s == None or s == '':
            #print("sn_down open url failed ", durl)
            continue
        wStr=''
        for i in range(0, len(s)):
            strUTF8=sat_util.ToUTF8(s[i])
            slist=insCode+','+strUTF8
            wStr += slist
        if wStr != '':
            f.writelines(wStr)


#http://table.finance.yahoo.com/table.csv?s=000001.sz
        
#http://biz.finance.sina.com.cn/stock/flash_hq/kline_data.php?
#&rand=random(10000)&symbol=sz002241
#&end_date=20130806&begin_date=20130101&type=plain

def TestHis():
    codes=sat_util.GetAllCodesFromCSV()
    qcodes=codes[0:1]
    now = datetime.datetime.now()
    start= datetime.date(2011,9,1)
    hisSina = sat_util.CreateFileNameByDate("util/his_sina_",now, start)
    f=open(hisSina, "w", encoding='utf-8')
    for i in range(0, len(qcodes)):
        SinaDownHistory(qcodes[i],now, start,f)
    
if __name__ == '__main__':
    start = time.time()
    #Test()
    TestHis()
    end = time.time()
    print("sina down s %d" %(end - start))
