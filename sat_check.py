#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

# sat_check.py
# 
"""
检查算法： 
1、对所有的算法进行验证（检验），采用历史数据验证历史数据,最终验证未来数据
2、比如000001代码使用算法AlgoMACD, 使用2001年的数据，验证2002年一月的股价。是否会满足涨或者跌的预测。如果满足继续验证所有的数据，并且对每一个验证进行积分，当积分达到设定值，说明该算法‘大概率’满足这只股票。
3、每只股票都需要采用不同的算法进行检查（验证），股票满足越多的算法，那么可以评定为稳定型股票，相应的风险在概率上就越低。
4、对某股票所有的算法都不满足，那么这只股票也可以关注。
5、如果股票的数据一部分满足某些算法，有些不满足，这种情况比较复杂，估计大部分股票都是这种情况。 此时就是体现验证算法的牛逼了，如果能验证或者推测出该股票在未来某个时间段中满足什么算法。这个是最终要求。
加一个时间限制
"""

"""
1、买和卖的算法不一致，或者是同一个算法，check可以把买卖两个函数作为参数，这样就解决了一个算法必须作为买卖的缺点。

"""
import time
import datetime
import sat_algo
import sat_ta
import sat_math
import sat_dbop
import sat_trade

"""
global var
"""
MinDataNum = 30

debug=True
#debug=False


class PosItem():
    def __init__(self,pos=0,price=0.0, date='1990-01-01', trade='wait'):
        self.pos=pos #交易位置
        self.price=price #交易价格
        self.trade=trade #交易类型，buy,sell 一般只保存买与卖
        self.date=date
    def PrintPosItem(self):
        print(self.pos, self.price, self.trade, self.date)

class CalcTradePos():
    def __init__(self, code, ltradePos=[], buySellStart=0, buySellEnd=250):
        self.code=code
        self.buySellStart=buySellStart
        self.buySellEnd=buySellEnd
        self.ltradePos=ltradePos
        #可以先判断买卖算法是否是一致，如果是一致的，只需要合并就可以 TODO
        self.ldifPos=[] #lbuyPos[i]-lsellPos[i]
        self.lyieldRate=[]#收益比例
        self.lbuyPos=[] #买点
        self.lsellPos=[] #卖点
        self.lbuyPrice=[] #买入价
        self.lsellPrice=[] #卖出价
        #self.statYieldRate = [] #统计收益率和，取最大值
        #self.lN=[]
        self.CalcDifPos()

    def getTradeSize(self):
        return len(self.ltradePos)

    def PrintCheck(self):
        print("print check start----------------")
        n=len(self.ldifPos)
        if (n > 0):
            print('dif Pos len', len(self.ldifPos), self.ldifPos,'\ndif: max,min,avg', max(self.ldifPos), min(self.ldifPos), sum(self.ldifPos)/len(self.ldifPos))
            if (len(self.lbuyPrice)):
                print('buy pos', self.lbuyPos)
                print('buy price max,min,avg: ', self.lbuyPrice,max(self.lbuyPrice),min(self.lbuyPrice),sum(self.lbuyPrice)/len(self.lbuyPrice))
            print('sell pos', self.lsellPos)
            if (len(self.lsellPrice)):
                print('sell price: max,min,avg', self.lsellPrice,max(self.lsellPrice),min(self.lsellPrice),sum(self.lsellPrice)/len(self.lsellPrice))
            print('code=, yieldRate, sum,max,min,avg=',self.code, self.lyieldRate, sum(self.lyieldRate), max(self.lyieldRate), min(self.lyieldRate), sum(self.lyieldRate)/len(self.lyieldRate))
        print("print check end----------------")

    def W2Mysql(self, algoName):
        nTradeSize = len(self.ltradePos)
        for i in range(0, nTradeSize):
            pos = self.ltradePos[i]
            dtStr = pos.date+' '+time.strftime('%H:%M:%S')
            dt = datetime.datetime.strptime(dtStr,'%Y-%m-%d %H:%M:%S')
            t = sat_trade.TradeItem(self.code, pos.price, 600, dt, pos.trade)
            t.W2Mysql(algoName)

    def CalcDifPos(self):
        nTrade=self.getTradeSize()
        if (debug):
            print('-----------start calc dif pos---------')
            print('code buy sell point and nTrade', self.code, self.buySellStart, self.buySellEnd, nTrade)
            for i in range(0, nTrade):
                self.ltradePos[i].PrintPosItem()
            print('-----------end calc if pos----------')
        #1、连续的买，连续的卖
        #2、买多卖少，买少卖多
        #找第一个买点，然后找第一个卖点，然后循环
        bBuy=False
        bSell=True
        buyPoint=PosItem()
        sellPoint=PosItem()
        for i in range(0, nTrade): 
            if (bSell and self.ltradePos[i].trade == 'buy'):
                buyPoint = self.ltradePos[i]
                bBuy=True
                bSell=False
            elif(bBuy and self.ltradePos[i].trade == 'sell'):
                sellPoint=self.ltradePos[i]
                bBuy=False
                bSell=True
                if sellPoint.price > 0 and buyPoint.price > 0:
                    #if (buyPoint.pos - sellPoint.pos) > 4:
                    #    continue
                    self.ldifPos.append(buyPoint.pos-sellPoint.pos)
                    self.lbuyPos.append(buyPoint.pos)
                    self.lsellPos.append(sellPoint.pos)
                    self.lbuyPrice.append(buyPoint.price)
                    self.lsellPrice.append(sellPoint.price)
                    self.lyieldRate.append(((sellPoint.price-buyPoint.price)/buyPoint.price) * 100)
                
        self.PrintCheck()

#check algo by history data
class SAT_CheckAlgo():
    def __init__(self, larv, lp, buySellStart=0, buySellEnd=250):
        self.code=larv[0].code
        self.AlgoChange=[] #算法名称和机会
        self.lp = lp #当前价格列表
        self.ldate=[] 
        self.ldate=sat_dbop.RSingleFromRedis(self.code,'date',-1)#当前日期列表
        if (0 == len(self.ldate)):
            print('get ', code, ' date failed')
            return None
        self.larv = larv
        self.larvLen = len(larv)
        self.buySellStart=buySellStart
        self.buySellEnd=buySellEnd
        self.ltradePos=[]
        self.run()
    
    def addTrade(self, PosItem):
        self.ltradePos.append(PosItem)
    #倒序
    def addTradeDesc(self, PosItem):
        self.ltradePos.insert(0, PosItem)

    def setBuySellEnd(self):
        maxSize = self.buySellEnd
        for i in range(0, self.larvLen):
            ljudgeData = self.larv[i].ljudgeData
            ljudgeDataLen = len(ljudgeData)
            if 1 < ljudgeDataLen and ljudgeData[0]:
                for j in range(1, ljudgeDataLen):
                    #if debug: print('name judgedate index, size', self.larv[i].indi, i, ljudgeData[j].size)
                    if (maxSize > ljudgeData[j].size):
                        maxSize = ljudgeData[j].size
            else:
                print('algo judge data error: ', self.larv[i].indi) 
                maxSize = 0
        print('buySellEnd, max judge data', self.buySellEnd, maxSize)
        self.buySellEnd = maxSize

    def resetJudgeData(self, index, pos):
        ljudgeData = self.larv[index].ljudgeData
        ljudgeDataLen = len(ljudgeData)
        ljudgeDataNew = [False]
        if 1 < ljudgeDataLen and ljudgeData[0]:
            ljudgeDataNew[0] = True
            #self.larv[index].ljudgeData[0] = True
            for i in range(1, ljudgeDataLen): 
                size = ljudgeData[i].size
                if debug:
                    #print('size, pos', size, pos)
                    #print('ljudgeData:',self.larv[index].indi, i, ljudgeData[i])
                    if size < pos:
                        print('out index size, pos ', size, pos)
                if (size > pos):
                    if pos == 0:
                        ljudgeDataNew.append(ljudgeData[i]) #here 
                    elif pos > 0:
                        ljudgeDataNew.append(ljudgeData[i][1:])

                #self.larv[index].ljudgeData[i] = self.larv[index].ljudgeData[i][pos:]
        self.larv[index].ljudgeData = ljudgeDataNew
        self.larv[index].chance = 'wait'


    def saveTradePos(self):
        if (debug): print('chech run: code', self.code, ' buy sell point range=', self.buySellStart, self.buySellEnd)
        #这个循环是反向的，因为最开始买卖点在buySellEnd处,buySellStart是最新的位置
        b = False
        algoFunc = None
        print('larv len', self.larvLen)
        self.setBuySellEnd()
        if debug: print('buySellEnd: start, end ', self.buySellStart, self.buySellEnd)
        for pos in range(self.buySellStart, self.buySellEnd):
            larvRet=[]
            for index in range (0, self.larvLen):
                #print('saveTradePos', index, pos)
                self.resetJudgeData(index, pos) #index, pos
                b, algoFunc = sat_algo.GetAlgoFunc(self.larv[index].indi)
                if b:
                    algoFunc(self.larv[index])
                    larvRet.append(self.larv[index])
                else:
                    print('error algoFunc', self.larv[index].indi)
            for i in range(0, len(larvRet)):
                print('pos i', pos, i, larvRet[i].chance)
            sat_algo.JudgeMulti(larvRet)
            #不管是买或卖，都放入PosItem
            #使用反序，从最近开始卖，然后再找买点。
            self.addTradeDesc(PosItem(pos, self.lp[pos], self.ldate[pos], self.larv[0].chance)) #应该循环所有的买之后再判断是否满足要求
    def run(self):
        self.saveTradePos()
        CalcTradePos(self.code, self.ltradePos, self.buySellStart, self.buySellEnd)

    
######################################################################################


""" 
计算不同代码，不同指标的参数的最合适值的意义：
1 根据极限理论，在不同买卖区间下，不同参数下，计算出最高‘收益率和’的序列，然后得到其参数
2 把所有的N组成一个序列，并且取其标准差，平均值
3 使用参数序列的‘一个标准差+平均值’作为最优参数， 可以把标准差大于3的去掉
 
"""
# calc algo params 
def CalcWRParams(codes):
    n=len(codes)
    buySellPointMin = 6
    buySellPointMax = 60
    buySellStep = 3
    paramMin = 3 
    paramMax = 20
    yieldRateMin = 0.03

    dRet = {}
    for i in range(0, n):
        lN=[]
        for k in range(buySellPointMin, buySellPointMax, buySellStep):#point
            #print("----------------------------")
            print('buySellPointMax = ', k)
            lcheck=[]
            for j in range(paramMin, paramMax): #N=?
                lcheck.append(CheckWR(codes[i], N=j, buySellEnd=k)) #600383
            lyieldRate=[]
            for rate in range(0, len(lcheck)):
                lyieldRate.append(sum(lcheck[rate].lyieldRate))
            #if (len(lyieldRate) > 0):
                #print('lyieldRate len, max,min,avg', lyieldRate,len(lyieldRate), max(lyieldRate),min(lyieldRate), sum(lyieldRate)/len(lyieldRate))
            maxV = max(lyieldRate)
            if (maxV < yieldRateMin):
                print('buy sell point range =', k, 'nothing')
                continue
            for sumV in range(0, len(lyieldRate)):
                if (maxV == lyieldRate[sumV]):
                    lN.append(sumV+paramMin)
            #print("-------------------------------")
        if len(lN) > 0:
            aN = sat_math.np.zeros(len(lN))
            for iN in range(0 ,len(lN)):
                aN[iN] = lN[iN]
            print("code, lN: std, avg, max,min", codes[i], lN, aN.std(), aN.mean(), aN.max(), aN.min())
            dRet[codes[i]]='std,avg,max,min:' + str(aN.std())+',' + str(aN.mean()) + ','+ str(aN.max())+','+str(aN.min())
            #save to t_algo_params
            lparams=[aN.std()+aN.mean()]
            lrangeData=[aN.std(), aN.mean(), aN.max(), aN.min()]
            sat_dbop.WAlgoParams2Mysql(codes[i], 'wr', lparams, lrangeData)
    print('total:', dRet)


######################################################################################
## check algo
def PublicCheck(code, ldata, lAlgoNameBuy=[], lAlgoNameSell=[], dAlgoParamsBuy={}, dAlgoParamsSell={}, buySellStart=0, buySellEnd=250):
    larvBuy = sat_algo.BuildAlgo(code, ldata, lAlgoNameBuy, dAlgoParamsBuy)
    larvSell = sat_algo.BuildAlgo(code, ldata, lAlgoNameSell, dAlgoParamsSell)
    if ((0 == len(larvBuy)) or (0 == len(larvSell))):
        print('public check error', larvBuy, larvSell)
        return None
    if (debug): print('larv', larvBuy, larvSell)
    #if (debug): print('ljudgeDataBuy',larvBuy[0].ljudgeData)
    #if (debug): print('ljudgeDataSell',larvSell[0].ljudgeData)
    #TODO 
    return SAT_CheckAlgo(larvBuy, ldata[0], buySellStart, buySellEnd)


def CheckMACD(code, ldata, FastN=12, SlowN=26, M=9, buySellStart=0, buySellEnd=250):
    print('check macd ', code)
    lAlgoNameBuy=['macd']
    lAlgoNameSell = ['macd']
    dAlgoParamsBuy={'macd':[FastN,SlowN,M]}
    dAlgoParamsSell={'macd':[FastN,SlowN,M]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)

        

def CheckRSI(code, ldata, N=14, buySellStart=0, buySellEnd=250):
    print('check rsi', code)
    lAlgoNameBuy=['rsi']
    lAlgoNameSell = ['rsi']
    dAlgoParamsBuy={'rsi':[N]}
    dAlgoParamsSell={'rsi':[N]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)
    
    

def CheckWR(code, ldata, N=14, buySellStart=0, buySellEnd=250):
    if (debug): print('check wr code, buySellStart, buySellEnd=', code, buySellStart, buySellEnd)
    lAlgoNameBuy=['wr']
    lAlgoNameSell = ['wr']
    dAlgoParamsBuy={'wr':[N]}
    dAlgoParamsSell={'wr':[N]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)
    


def CheckCCI(code, ldata, N=14, buySellStart=0, buySellEnd=250):
    print('check cci', code)
    lAlgoNameBuy=['cci']
    lAlgoNameSell = ['cci']
    dAlgoParamsBuy={'cci':[N]}
    dAlgoParamsSell={'cci':[N]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)



def CheckROC(code, ldata, FastN=6, SlowN=12, buySellStart=0, buySellEnd=250):
    print('check roc', code)
    lAlgoNameBuy=['roc']
    lAlgoNameSell = ['roc']
    dAlgoParamsBuy={'roc':[FastN, SlowN]}
    dAlgoParamsSell={'roc':[FastN, SlowN]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)
    

def CheckKDJ(code, ldata, N=9,M1=3,M2=3, buySellStart=0, buySellEnd=250):
    print('check kdj', code)
    lAlgoNameBuy=['kdj']
    lAlgoNameSell = ['kdj']
    dAlgoParamsBuy={'kdj':[N,M1,M2]}
    dAlgoParamsSell={'kdj':[N,M1,M2]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)
    


def CheckBOLL(code, ldata, N=14, buySellStart=0, buySellEnd=250):
    print('check boll', code)
    lAlgoNameBuy=['boll']
    lAlgoNameSell = ['boll']
    dAlgoParamsBuy={'boll':[N]}
    dAlgoParamsSell={'boll':[N]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)

def CheckSAR(code, ldata, N=4, step=0.02, maxAF=0.2, buySellStart=0, buySellEnd=250):
    print('check sar', code)
    lAlgoNameBuy=['sar']
    lAlgoNameSell = ['sar']
    dAlgoParamsBuy={'sar':[N,step,maxAF]}
    dAlgoParamsSell={'sar':[N,step,maxAF]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)


def CheckWR_KDJ(code, ldata, N=14, N1=9, M1=3, M2=3, buySellStart=0, buySellEnd=250):
    print('check wr_kdj', code)    
    lAlgoNameBuy=['wr','kdj']
    lAlgoNameSell = ['wr','kdj']
    dAlgoParamsBuy={'wr':[N],'kdj':[N1,M1,M2]}
    dAlgoParamsSell={'wr':[N],'kdj':[N1,M1,M2]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)
   
def CheckKDJ_DMI(code, ldata, dmiN=14, dmiN1=6,dmiN2=14, N1=9, M1=3, M2=3, buySellStart=0, buySellEnd=250):
    print('check kdj_dmi', code)
    lAlgoNameBuy=['dmi','kdj']
    lAlgoNameSell = ['dmi', 'kdj']
    dAlgoParamsBuy={'dmi':[dmiN,dmiN1,dmiN2], 'kdj':[N1,M1,M2]}
    dAlgoParamsSell={'dmi':[dmiN,dmiN1,dmiN2], 'kdj':[N1,M1,M2]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)

def CheckKDJ_WR(code, ldata, N=14, N1=9, M1=3, M2=3, buySellStart=0, buySellEnd=250):
    print('check kdj_wr', code)
    lAlgoNameBuy=['wr','kdj']
    lAlgoNameSell = ['wr', 'kdj']
    dAlgoParamsBuy={'wr':[N], 'kdj':[N1,M1,M2]}
    dAlgoParamsSell={'wr':[N], 'kdj':[N1,M1,M2]}
    return PublicCheck(code, ldata, lAlgoNameBuy, lAlgoNameSell, dAlgoParamsBuy, dAlgoParamsSell, buySellStart, buySellEnd)
    
    
 
if __name__ == '__main__':
    start = time.time()
    #c,codes=sat_algo.GetCodesBySingleKeyLimit('*cur', 2, 20)
    # jugl 000959, 600715, 002391, 600156
    codes= ['601000']#
    n=len(codes)
    lcheck=[]
    for i in range(0, 1):
        ldata=sat_algo.GetSrcDataByIndi(codes[i], 'kdj')
        #print('ldata',ldata)
        #lcheck.append(CheckWR(codes[i],ldata, N=13))
        lcheck.append(CheckKDJ_DMI(codes[i], ldata, buySellEnd=500))
        #lcheck.append(CheckKDJ_WR(codes[i], ldata, buySellEnd=250))
    #for i in range(0, len(lcheck)):
        #lcheck[i].PrintCheck()
     #   lcheck[i].W2Mysql('kdj')
    #CalcWRParams(codes)
    #dtStr = '2014-01-01'+' '+time.strftime('%H:%M:%S')
    #dt = datetime.datetime.strptime(dtStr,'%Y-%m-%d %H:%M:%S')
    #print(dtStr,dt)
    end = time.time()
    print("total seconds %d" %(end - start))

#6 600882 600715 600336 002391
#4 000959 
#8 002708
#3 600586 
#5 600156 最大点买的
