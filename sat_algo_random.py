#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

# sat_algo_random.py
# 随机算法
 
"""
"""
import time
import random

debug = True
#debug = False
from sat_algo_public import *

#1 random algo simple
#return dict, because not dup
def GetRandomStockCodes(codes, top):
    num = len(codes)
    ret = []
    d = {}
    for i in range(0, top):
        while True:
            i=random.randint(0, num)
            if i < num and (None == d.get(codes[i])):
                d[codes[i]]=codes[i]
                break
    for i in d:
        ret.append(str(i))
    return ret

#自然（完全）随机算法
def AlgoNaturalRandom(top):
    codes = GetAllCodes()
    if (debug): print(len(codes))
    codes = GetRandomStockCodes(codes, top)
    if (debug):
        for i in range(0, len(codes)):
            print(codes[i])
    lrp=GetAllPrice(codes)
    ShowSimpleStockInfo(lrp)
    
def GetCodesBySingleKeyLimit(key, min, max):
    kv = rh.keys(key)
    c=0
    codes = []
    for i in range(0,len(kv)):
        v = rh.lindex(kv[i], 0)
        f=float(v)
        if f >= min and f <= max:
            codes.append(str(kv[i])[2:8])
            #if (debug): print('kv: ', str(kv[i][:6]), f)
            c +=1
    return c,codes

#2 random algo 随机取满足条件的股票，比如按要求涨跌，参数是一个指标和一个区间 
def AlgoSingleLimitRandom(k, min=0, max=100, top = 10):
    c,codes=GetCodesBySingleKeyLimit(k, min, max)
    if (debug):
        for i in range(0, len(codes)):
            print('single:', codes[i])
    if (len(codes) > top):
        codes = GetRandomStockCodes(codes, top)
    lrp=GetAllPrice(codes)
    ShowSimpleStockInfo(lrp)
    print('total: ', c)



#support multi condition(or,and,union)
# todo support plate type, condition is dict keys, dkeys like {'1':{'*updown, 5, 10}, '2':{*cur, 3, 10}, ...}
def AlgoMultiLimitRandom(dkeys, top = 10):
    if(debug): print('multi')
    codes=[]
    dRet = {}
    dsize = 0
    for k in dkeys:
        if (debug): print(k, dkeys[k], dkeys[k]['0'], dkeys[k]['1'], dkeys[k]['2']) 
        c,tmpcodes=GetCodesBySingleKeyLimit(dkeys[k]['0'],dkeys[k]['1'],dkeys[k]['2'])
        dsize += 1
        #if (debug): print('len(tmpcodes) ', c)
        for i in range(0, len(tmpcodes)):
            if not dRet.get(tmpcodes[i]):
                # if (debug): print(dRet[tmpcodes[i]])
                dRet[tmpcodes[i]] = 1
            else:
                v=dRet[tmpcodes[i]]
                v+=1
                dRet[tmpcodes[i]]=v
                if (debug): print(tmpcodes[i], v)
    #dRet.sorted(dRet.values, reversed=True)
    n= 0
    if (debug):  print('dsizem dRet', dsize, len(dRet))
    for k in dRet:
        #if (debug): print('type k:', type(k), 'k=', k, 'v=', dRet[k])
        if (dRet[k] >= dsize):
            codes.append(str(k))
            n += 1
    if (debug): print('n= ', n, 'codes len ', len(codes))
    if (len(codes) > top):
        print('random codes', len(codes), top)
        codes = GetRandomStockCodes(codes, top)
    print('codes: ', len(codes))
    lrp=GetAllPrice(codes)
    ShowSimpleStockInfo(lrp)

"""
get basic indicator
public function
"""    
#freq=30, 理论上30个以上就能达到最低要求的数量
#返回每个代码的平均值和标准差,返回两个列表，
def GetCodesAvgStdByFreq(codes, indicator='cur', freq=30):
    n = len(codes)
    if n <= 0 or n > maxStocks:
        print("codes invalid")
        return None, None
    if freq < 30:
        freq = 30
    lavg=[]
    lstd=[]
    for i in range(0, n):
        srcData=sat_dbop.RSingleNumFromRedis(codes[i], indicator, freq)
        srcLen=len(srcData)
        if srcLen > 0:
            u=sat_math.List2npArray(srcData) #np.array()
            lavg.append(u.mean())
            lstd.append(u.std())
        else:
            lavg.append(-1)
            lstd.append(-1)
    return lavg,lstd

#获取每个代码的最新价，返回一个列表
def GetCodesNewPriceFromRedis(codes):
    n = len(codes)
    if (n <= 0):
        return None
    lret=[]
    for i in range(0, n):
        lsrcData=sat_dbop.RSingleNumFromRedis(codes[i], 'cur', 0)
        if (len(lsrcData) > 0):
            lret.append(lsrcData[0])
        else:
            lret.append(-1) #表示无效值
    return lret


#算法1，当前价格在某个范围，并且小于历史平均值，其标准差满足自定义要求
def AlgoByAvgStdPrice(pmax=100,pmin=0.1,vmin=0.01,top=300, stdmax=10,stdmin=0):
    codes = GetAllCodes()
    n = len(codes)
    lretcodes=[]
    lretprice=[]
    lpricecodes=[]
    lcur=[]
    c = 0
    lprice=GetCodesNewPriceFromRedis(codes)
    if lprice == None:
        print("get new price faild")
        return None
    for i in range(0, n):
        if (lprice[i] >= pmin and lprice[i] <= pmax):
            lpricecodes.append(codes[i])#满足要求的代码
            lcur.append(lprice[i])
    lavg,lstd=GetCodesAvgStdByFreq(lpricecodes, 'cur', top)
    n = len(lpricecodes)
   #算法，把最新值小于平均值的代码列出来
    for i in range(0, n):
        if (lcur[i] < (lavg[i]-vmin)  and lstd[i] >= stdmin and lstd[i] <= stdmax):
            if (debug): print(lpricecodes[i], lcur[i], lavg[i], lstd[i])
            lretcodes.append(lpricecodes[i])
            lretprice.append(lcur[i])
 
    print('total num =', len(lretprice))
    return lretcodes, lretprice

#把波动率小于历史波动率的计算出来 TODO
def AlgoVRange(codes, freq=30, max=10,  min=0):
    n = len(codes)
    lret=[]
    lcur=[]
    lu=[]
    c=0
    for i in range(0, n):
        srcData=sat_dbop.RSingleNumFromRedis(codes[i], 'cur', freq)
        srcLen=len(srcData)
        if srcLen > 0:
            u =sat_math.CalcYield(srcData)
            lcur.append(srcData[0])
            lu.append(u)
    #for i in range(0, len(lu)):

######################################################################
""" 设定条件 类似于背包问题，1表示背包大小，2表示最大价值，还有一个约束是消耗费
1 初始值starting value
2 预期值expected value（预期收益）2-1/1 就是收益率
3 手续费counter                                                                                                                                                                                                                                                                                          fee
TODO ： 这个功能可以后面做，
""" 
######################################################################

def CalcExpectedYield(code, indicator, n):
    lret = sat_dbop.RSingleNumFromRedis(code, indicator, n)
    #if (debug): print(lret)
    if len(lret) > 0:
        u = sat_math.List2npArray(lret)
        uY = sat_math.CalcYield(u)
        if (debug): 
            print("code ", code)
            print('price is dup', (u[0] - u.mean())/u.std())
            print('yield is dup', (uY[0] - uY.mean())/uY.std())
            sat_math.GenIndiPrint(u)
        e,v,r = sat_math.CalcExpected(u[0], u)
        print('expected yield =', e,v,r)

def TestYield():
    code= '600586' #'600221' #000089 600586
    indicator = 'cur'
    CalcExpectedYield(code, indicator, 1000)

def Test():
    codes = []

if __name__ == '__main__':
    start = time.time()
    #AlgoNaturalRandom(4)
    #AlgoSingleLimitRandom('*cur', 5, 10, 2)
    #dkeys = {"1" : {"0":"*updownrate", "1":9, "2":11}, "2" : {"0":"*cur","1":3, "2":10},"3" : {"0":"*updown", "1":0.4, "2":10}}
    dkeys = {"1" : {"0":"*cur", "1":9, "2":11}, "2" : {"0":"*cur","1":3, "2":10}}
    #AlgoMultiLimitRandom(dkeys, 5)
    #TestYield()
    AlgoByAvgStdPrice(10,5)
    end = time.time()
    print("total seconds %d" %(end - start))

