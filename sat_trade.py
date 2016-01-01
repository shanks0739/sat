#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

# sat_trade.py
# trade records

import time
import datetime
import csv
import sat_algo
import sat_dbop
import sat_cmysql

"""
global var
"""
debug = True
#debug = False

tradeRecords = "util/trade_records.csv"
fTrade = open(tradeRecords, 'a', encoding='utf8')
now = datetime.datetime.now()

stockMinNum=100
buyFee = 0.03
sellFee = 0.04
dStopLossPoint = 0.1 #默认止损点
dStopProfitPoint = 0.08 #默认止盈点
dPriceMax = 20


#1 trade ， input: sizeM  output: (code,p,num,datetime,cost,tradeflag)
"""
1 买卖什么 2 买卖多少 3 买卖价格 4 何时买卖
5 止损点 6 止盈点 7 买卖策略
"""
class TradeItem():
    def __init__(self, code, price, num=100, dtTrade=None, flag='buy'):
        self.code=code #买卖什么
        self.price=price #买卖价格
        self.num=num #买卖数量
        self.money=float(self.price) * float(self.num) #买卖资金
        self.flag=flag #买卖标识，buy or sell
        if self.flag=='buy':
            self.money += self.money * buyFee
        elif self.flag=='sell':
            self.money += self.money * sellFee
        if dtTrade == None:
            dtTrade = now
        self.datetime=dtTrade #买卖时间
    
    def W2CSV(self, f):
        if (debug): print(self.PrintTrade())
        lrecord=[self.code, str(round(self.price,2)), str(round(self.num,0)), str(round(self.money,4)), self.datetime.strftime('%Y-%m-%d %H:%M:%S'),self.flag]
        print(','.join(lrecord), file=f)

    def W2Mysql(self,algo=''):
        inHead = "insert ignore into t_trade(code,price,num,money,date,time,bsflag,algo) values(%s,%s,%s,%s,%s,%s,%s,%s)"
        l=[self.code, str(round(self.price,2)), str(round(self.num,0)), str(round(self.money,4)), self.datetime.strftime('%Y-%m-%d'),self.datetime.strftime('%H:%M:%S'),self.flag,algo]
        print("save trade mysql")
        sat_cmysql.Insert(inHead,l)
   
        
    def PrintTrade(self):
        print('trade', self.code,self.flag,self.price,self.num,self.money)

def HandInputTradeInfo2CSV(code, price, num=100, dtTrade=now,flag='buy'):
    t = TradeItem(code,price,num,dtTrade,flag)
    t.W2CSV(fTrade)

def HandInputTradeInfo2Mysql(code, price, num=100, dtTrade=now,flag='buy'):
    t = TradeItem(code,price,num,dtTrade,flag)
    t.W2Mysql('dmi_bbi_vol')

#保存交易信息，这个函数用来处理算法得出的代码，保存买点，之后看看算法得出的代码的表现怎样
#这个最终是要存表的，目前存入文件中
def AutoSaveTradeInfo(codes, num=200):
    #获取当前股票价格
    lprice = sat_dbop.RCurPriceFromRedis(codes)
    for i in range(0, len(lprice)):
        print('code, cur', codes[i], lprice[i])
        HandInputTradeInfo2CSV(codes[i], lprice[i], num)
        HandInputTradeInfo2Mysql(codes[i], lprice[i],num)

#把csv文件的交易数据导入表中
def RCSV2Mysql():
    ltrade=[]
    c = csv.reader(open(tradeRecords, 'r', encoding='utf8'))
    for code,price,num,money,dtTrade,flag in c:
        if (debug): 
            print(code,price,num,money,dtTrade,flag)
        DtTrade = datetime.datetime.strptime(dtTrade,'%Y-%m-%d %H:%M:%S')
        ltrade.append(TradeItem(code,float(price),float(num),DtTrade,flag))
    for i in range(len(ltrade)):
        ltrade[i].W2Mysql('kdj,wr(13,34,89)')

####################################################################################
#以下等自动交易完成后，TODO
#class SAT_Buy():
#    def __init__(self, money=2000, stopLoss=dStopLossPoint, stopProfit=dStopProfitPoint):
#        self.stopLossPoint = stopLoss
#        self.stopProfitPoint = stopProfit
#        self.buyCodes = self.getBuyCodes(money)
#        self.strategy = None #买卖策略，使用的是wr,kdj,sar???
#        
#        #init buy item
#        self.lbuy = [] #TradeItem('000001','2015-01-13',15)
#        self.InitBuy()
#        self.W2CSVBuyRecords()
#    
#    def InitBuy(self):
#         #获取当前股票价格
#        lprice = sat_dbop.RCurPriceFromRedis(self.buyCodes)
#        now = datetime.datetime.now()
#        for i in range(0, len(lprice)):
#            print('code, cur',self.buyCodes[i], lprice[i])
#            self.lbuy.append(TradeItem(self.buyCodes[i], lprice[i], dtTrade=now))
#
#    def W2CSVBuyRecords(self):
#        for i in range(0, len(self.lbuy)):
#            #print(self.lbuy[i].PrintTrade())
#            self.lbuy[i].W2CSV(fTrade)
#
#    def getBuyCodes(self, money):
#        priceMax = money/stockMinNum #不计算手续费，是因为可以在买卖点设置低一些
#        if priceMax > dPriceMax:
#            priceMax = dPriceMax
#        c,codes=sat_algo.GetCodesBySingleKeyLimit('*cur', 2, priceMax)
#        print("buy codes",len(codes))
#        self.strategy = 'wr'
#        print("TODO use sat_alog methon")
#        return codes


if __name__ == '__main__':
    start = time.time()
    #c,codes=GetCodesBySingleKeyLimit('*cur', 3, 10)
    codes=   ['600589', '000928', '600125', '002317', '600598', '000042', '000619', '600239', '600493', '600097', '000875', '002225', '002433', '200613', '600217', '600469', '002247', '600744', '002468', '600630', '600131', '000560', '002407', '002206', '600488', '000012', '000610', '000737']
    print('code size', len(codes))
    dtTrade = datetime.datetime.strptime('2015-01-13','%Y-%m-%d')
    #HandInputTradeInfo('000001',15.00, 100, dtTrade ,'buy')
    AutoSaveTradeInfo(codes, 600)
    #RCSV2Mysql()
    end = time.time()
    print("total seconds %d" %(end - start))


fTrade.close()
