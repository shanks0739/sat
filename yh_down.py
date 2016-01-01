#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

"""
yahoo 每5秒刷一次数据
download data from yahoo.
查询大盘指数，比如查询上证综合指数（000001）：
以 , 分割字符串中内容，下标从0开始，依次为
http://finance.yahoo.com/d/q.csv?s=000001.sz,000002.sz&f=snd2c8ghopn4
雅虎股票API f参数对照表
a	Ask	a2	Average Daily Volume	a5	Ask Size
b	Bid	b2	Ask (Real-time)	b3	Bid (Real-time)
b4	Book Value	b6	Bid Size	c	Change & Percent Change
c1	Change	c3	Commission	c6	Change (Real-time)
c8	After Hours Change (Real-time)	d	Dividend/Share	d1	Last Trade Date
d2	Trade Date	e	Earnings/Share	e1	Error Indication (returned for symbol changed / invalid)
e7	EPS Estimate Current Year	e8	EPS Estimate Next Year	e9	EPS Estimate Next Quarter
f6	Float Shares	g	Day’s Low	h	Day’s High
j	52-week Low	k	52-week High	g1	Holdings Gain Percent
g3	Annualized Gain	g4	Holdings Gain	g5	Holdings Gain Percent (Real-time)
g6	Holdings Gain (Real-time)	i	More Info	i5	Order Book (Real-time)
j1	Market Capitalization	j3	Market Cap (Real-time)	j4	EBITDA
j5	Change From 52-week Low	j6	Percent Change From 52-week Low	k1	Last Trade (Real-time) With Time
k2	Change Percent (Real-time)	k3	Last Trade Size	k4	Change From 52-week High
k5	Percebt Change From 52-week High	l	Last Trade (With Time)	l1	Last Trade (Price Only)
l2	High Limit	l3	Low Limit	m	Day’s Range
m2	Day’s Range (Real-time)	m3	50-day Moving Average	m4	200-day Moving Average
m5	Change From 200-day Moving Average	m6	Percent Change From 200-day Moving Average	m7	Change From 50-day Moving Average
m8	Percent Change From 50-day Moving Average	n	Name	n4	Notes
o	Open	p	Previous Close	p1	Price Paid
p2	Change in Percent	p5	Price/Sales	p6	Price/Book
q	Ex-Dividend Date	r	P/E Ratio	r1	Dividend Pay Date
r2	P/E Ratio (Real-time)	r5	PEG Ratio	r6	Price/EPS Estimate Current Year
r7	Price/EPS Estimate Next Year	s	Symbol	s1	Shares Owned
s7	Short Ratio	t1	Last Trade Time	t6	Trade Links
t7	Ticker Trend	t8	1 yr Target Price	v	Volume
v1	Holdings Value	v7	Holdings Value (Real-time)	w	52-week Range
w1	Day’s Value Change	w4	Day’s Value Change (Real-time)	x	Stock Exchange
y	Dividend Yield

"""
import time
import datetime
import random
import urllib
import urllib.request

import sat_util
import sat_down

#debug=False
debug = True


PriceDataLen = 31

def FillSingleDict(slist):
    yahooDict={}
    bRet = False
    if (len(slist) >= PriceDataLen):
        #print(len(slist))
        #只是返回一个字典
        yahooDict['opening'] = (slist[1]) #开盘价 
        yahooDict['closed'] = (slist[2]) #昨天收盘价
        yahooDict['cur'] = (slist[3])     # 当前价格
        yahooDict['highest'] = (slist[4])
        yahooDict['lowest'] = (slist[5])
        yahooDict['buy1'] = (slist[6])
        yahooDict['sell1'] = (slist[7])
        yahooDict['volume'] = (slist[8]) #总成交量
        yahooDict['turnover'] = (slist[9]) #总成交额（万）        
        yahooDict['buy1volume'] = (slist[10])
        #yahooDict['buy1'] = (slist[11])
        yahooDict['buy2volume'] = (slist[12])
        yahooDict['buy2'] = (slist[13])
        yahooDict['buy3volume'] = (slist[14])
        yahooDict['buy3'] = (slist[15])
        yahooDict['buy4volume'] = (slist[16])
        yahooDict['buy4'] = (slist[17])
        yahooDict['buy5volume'] =(slist[18])
        yahooDict['buy5'] = (slist[19])
        yahooDict['sell1volume'] = (slist[20])
        #yahooDict['sell1'] = (slist[21])
        yahooDict['sell2volume'] = (slist[22])
        yahooDict['sell2'] = (slist[23])
        yahooDict['sell3volume'] = (slist[24])
        yahooDict['sell3'] = (slist[25])
        yahooDict['sell4volume'] = (slist[26])
        yahooDict['sell4'] = (slist[27])
        yahooDict['sell5volume'] =(slist[28])
        yahooDict['sell5'] = (slist[29])
        yahooDict['date'] = slist[30] # date
        yahooDict['time'] = slist[31] #time
        yahooDict['code'] = slist[33] # 代码，应该不需要包含sz,sh,hk
        #下面是自己算的
        cur = float(slist[3])
        opening = float(slist[1])
        yahooDict['updown'] =  cur - opening#涨跌
        if (opening > 0.01):
            yahooDict['updownrate'] = (cur - opening) / opening #涨跌幅%
        else:
            yahooDict['updownrate'] = 0
        yahooDict['uplimit'] = opening * 1.1 #最高10%
        yahooDict['downlimit'] = opening * 0.9 #最低10%
        
        yahooDict['turnoverrate'] = 0 #换手率
        yahooDict['earningsrate'] = 0
        yahooDict['amplitude'] = 0
        yahooDict['pb'] = 0
        yahooDict['outdisk'] = 0
        yahooDict['indisk'] = 0
        
        bRet = True
        if (debug): print(slist[30], '  ', yahooDict['date'], '  ', yahooDict['time'])
    return bRet, yahooDict
 
#这个函数需要做成多态的形式，不同的来源，格式是不一样的。
def YahooParseSingle(s):  
    if(debug): print('YahooParseSingle', type(s))  
    slist=s[13:] #此处应该使用更好的方式
    code=slist[:6]
    if(debug): print(slist, code)  
    slist=slist.split(',')
    slist.append(code)
    if (debug): print(slist)
    return FillSingleDict(slist)
   
    

#所有的code，应该是不带有参数的，应该由各自转化为相应的合适完整请求代码  
qurl='http://'
qcodePrefix='&s='
qrandomPrefix='&r='
def yahooDown(code):
    code=sat_util.codeAddPrefix(code)
    durl=qurl+qrandomPrefix+str(random.random())+qcodePrefix+code
    if (debug): print(durl)
    s = sat_down.GetRtPriceByURL(durl)
    if s == '':
        return False,None
    strGB=sat_util.ToGB(s)
    return yahooParseSingle(strGB)


# 多个代码一起调用
def YahooParseMulti(s):  
    if(debug): print(type(str))
    ldict=[]
    for l in s:
        if (debug): print(l)
        strGB=sat_util.ToGB(l)
        b, d=YahooParseSingle(strGB)
        if b:
            ldict.append(d)
    return ldict


def YahooDownMulti(codes):
    qcode=''
    for i in range(0, len(codes)):
        qcode += sat_util.codeAddPrefix(codes[i]) +','
    durl=qurl+qrandomPrefix+str(random.random())+qcodePrefix+qcode
    if (debug): print(durl)
    s=sat_down.GetMultiRtPriceByURL(durl)
    if (debug): print(s, len(s))
    return YahooParseMulti(s)

def Test():
    codes=sat_util.GetAllCodesFromCSV()
    qcodes=codes[0:3]
    ldict=YahooDownMulti(qcodes)
    for i in range(0, len(ldict)):
        print(ldict[i])
    #b,d=yahooDown(codes[0])
    #print(b, d)

#http://table.finance.yahoo.com/table.csv?s=000001.sz
#s=ibm&d=6&e=22&f=2006&g=d&a=11&b=16&c=2005&
#特殊点是月份是0～11
qurlHis='http://table.finance.yahoo.com/table.csv?'
qcodePre='&s='
mStartPre='&a='
dStartPre='&b='
yStartPre='&c='
#linkEndStart='&g=d'
mEndPre='&d='
dEndPre='&e='
yEndPre='&f='
"""
"""
#Date,Open,High,Low,Close,Volume,Adj Close
#做成通用的，传入两个日期，一个代码，文件句柄，
#日期都是datetime.datetime类型now=datetime.datetime.now()
def YahooDownHistory(code, dtEnd, dtStart, f):
    code=sat_util.codeAddSuffix(code)
    qcode=code[0:6]+'.'+code[6:]
    insCode=qcode[:6]
    
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

    #倒序查询
    for i in range(yEnd, yStart-1, -1):
        if i == yEnd and i == yStart:
            qmEnd = mEndPre+str(mEnd-1)
            qdEnd = dEndPre+str(dEnd)
            qmStart = mStartPre+str(mStart-1)
            qdStart = dStartPre+str(dStart)
        elif i == yEnd and i > yStart:
            qmEnd = mEndPre+str(mEnd-1)
            qdEnd = dEndPre+str(dEnd)
            qmStart = mStartPre + '0'
            qdStart = dStartPre + '1'              
        elif i < yEnd and i > yStart:
            qmEnd = mEndPre + '11'
            qdEnd = dEndPre + '31'
            qmStart = mStartPre + '0'
            qdStart = dStartPre + '1'       

        elif i < yEnd and i == yStart:
            qmEnd = mEndPre + '11'
            qdEnd = dEndPre + '31'
            qmStart = mStartPre+str(mStart-1)
            qdStart = dStartPre+str(dStart)
        else:
            print("date error, give up this query")
            break
            
        qyEnd = yEndPre + str(i)
        qyStart = yStartPre + str(i)   
        qDate = qyEnd+qmEnd+qdEnd+qyStart+qmStart+qdStart
        durl=qurlHis+qcodePre+qcode+qDate
        if (debug): print(durl)
        s = sat_down.GetMultiRtPriceByURL(durl)
        if s == None or s == '':
            print("yahoo open url failed ", durl)
            continue
        wStr=''
        for i in range(1, len(s)):
            strUTF8=sat_util.ToUTF8(s[i])
            slist=insCode+','+strUTF8
            wStr += slist
        f.writelines(wStr)



def TestHis():
    codes=sat_util.GetAllCodesFromCSV()
    qcodes=codes[0:1]
    now = datetime.datetime.now()
    start= datetime.date(2014,12,1)
    hisYahoo = sat_util.CreateFileNameByDate("util/his_yahoo_",now, start)
    f=open(hisYahoo, 'w', encoding='utf-8')
    for i in range(0, len(qcodes)):
        YahooDownHistory(qcodes[i],now, start, f)
    
if __name__ == '__main__':
    start = time.time()
    #Test()
    TestHis()
    end = time.time()
    print("yahoo down s %d" %(end - start))
