#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

# sat_algo_public.py

import time
import sat_dbop
import sat_util
import sat_rtprice
import sat_dbop
import sat_math


#debug = True
debug = False

maxStocks=5000
r=sat_rtprice.r
rh=sat_rtprice.rh

#把算法的命名要求： Algo+自命名
#算法返回值结构: 代码，最新价，预计最低价（买入点），预计最高价，（卖出点）#每股收益率最大值，每股收益率最小值，每股收益最大值，每股收益最小值    
#每个算法计算的结果都应该使用这个类,也就是最关心的几个指标

#algo return value
class SAT_AlgoRV():
    def __init__(self, code, indiName, ljudgeData):
        self.code=code
        self.indi=indiName
        self.ljudgeData=ljudgeData#判断数据
        self.chance='wait' # buy, sell, wait, notice 

    def getCurCode(self):
        return self.code

    def setJudgeData(self, ljudgeData):
        self.ljudgeData=ljudgeData
    def setJudgeDataNull(self):
        self.ljudgeData=[]

    def getJudgeData(self):
        return self.ljudgeData

    #def algo(self):
    #    if None != self.func:
    #        if(debug): print(self.func, self.args)
    #        if (len(self.lcalcData) != 0):
    #            self.func(self)
    def isBuy(self):
        if (self.chance == 'buy'):
            return True
        return False
    def isSell(self):
        if (self.chance == 'sell'):
            return True
        return False
    def isWait(self):
        if (self.chance == 'wait'):
            return True
        return False
    def isNotice(self):
        if (self.chance == 'notice'):
            return True
        return False
    def isInvalid(self):
        if (self.chance == 'invalid'):
            return True
        return False
    
    def saveBuySellCode(self,lbuys=[],lsells=[]):
        if self.isBuy():
            lbuys.append(self.code)
        elif self.isSell():
            lsells.append(self.code)


    def PrintRetValue(self):
        print('code, indi, chance:', self.code, self.indi, self.chance)


#public func
def GetAllCodes():
    return sat_util.GetAllCodesFromCSV()

def GetAllPrice(codes):
    return sat_rtprice.GetPriceMulti(codes)

def ShowSimpleStockInfo(lrp):
    for i in range(0, len(lrp)):
        lrp[i].NameCodeCurUpdown()

    
def ShowAllStockInfo(lrp):
    for i in range(0, len(lrp)):
         lrp[i].PricePrint()

 


if __name__ == '__main__':
    start = time.time()
    arv = SAT_AlgoRV('000001', 'macd')
    #get data
    arv.algo()
    print(arv)
    end = time.time()
    print("total seconds %d" %(end - start))
