#!/usr/bin/env python3  
#coding=utf-8
# -*- coding:utf-8 -*-  


"""
 : 代码  3: 当前价格  
 7: 外盘  8: 内盘  
 31: 涨跌  32: 涨跌%  33: 最高  34: 最低   36: 成交量（手）  37: 成交额（万）  
 38: 换手率  39: 市盈率  40:    46: 市净率
 41: 最高  42: 最低  43: 振幅  
9: 买一  10: 买一量（手）  11-18: 买二 买五  
 19: 卖一  20: 卖一量  21-28: 卖二 卖五  
 30: 时间 
4: 昨收  5: 今开  47: 涨停价  48: 跌停价 （这几个指标要不要放到核心类中? 暂时放入）
"""

"""
use redis save real-time price, key/values(is list, insert(0,RealTimePrice))
focus,not focus, 

kernel data class （RtPrice）:
各种来源的实时数据转化为该数据类型
来源的数据保存到字典中，通过这个字典把数据存入该类中，
避免来源的数据顺序或者指标的名称不一样。

并提供保存到文件，mysql,redis的功能
"""   
import time
import datetime
import csv

import sat_util
import sat_thread
import sat_down
import sat_credis
import sat_cmysql

"""
golbal var
"""  
debug = False
#debug = True

r = sat_credis.r
rh = sat_credis.rh


partfile = "util/parttest.csv"
alltest = "util/alltest.csv"
#platefile = "util/plate.csv"
rtpfile = "util/RealTimePrice.csv"
#allhistory="util/allhistory.csv"    

"""
redis just support bytes, so not convert to 
"""     
class RtPrice:
    def __init__(self, dictPrice): #dict price data
        self.code = dictPrice['code'] # 代码，应该不需要包含sz,sh,hk
        self.cur =  dictPrice['cur']    # 当前价格
        self.updown = dictPrice['updown'] #涨跌  
        self.updownrate = dictPrice['updownrate'] #涨跌幅% 
        self.highest = dictPrice['highest']
        self.lowest = dictPrice['lowest']
        self.closed = dictPrice['closed'] #昨天收盘价
        self.opening = dictPrice['opening'] #开盘价
        self.volume = dictPrice['volume'] #成交量
        self.turnover = dictPrice['turnover'] #成交额
        self.turnoverrate = dictPrice['turnoverrate'] #换手率
        self.outdisk = dictPrice['outdisk'] #外盘
        self.indisk = dictPrice['indisk'] #内盘
        self.earningsrate = dictPrice['earningsrate'] #市盈率
        self.pb = dictPrice['pb'] #市净率
        self.amplitude = dictPrice['amplitude'] #振幅
        self.uplimit = dictPrice['uplimit'] #涨停价
        self.downlimit = dictPrice['downlimit']#跌停价
        self.buy1 = dictPrice['buy1']
        self.buy1volume = dictPrice['buy1volume']
        self.buy2 = dictPrice['buy2']
        self.buy2volume = dictPrice['buy2volume']
        self.buy3 = dictPrice['buy3']
        self.buy3volume = dictPrice['buy3volume']
        self.buy4 = dictPrice['buy4']
        self.buy4volume = dictPrice['buy4volume']
        self.buy5 = dictPrice['buy5']
        self.buy5volume =dictPrice['buy5volume']
        self.sell1 = dictPrice['sell1']
        self.sell1volume = dictPrice['sell1volume']
        self.sell2 = dictPrice['sell2']
        self.sell2volume =dictPrice['sell2volume']
        self.sell3 = dictPrice['sell3']
        self.sell3volume = dictPrice['sell3volume']
        self.sell4 = dictPrice['sell4']
        self.sell4volume =dictPrice['sell4volume']
        self.sell5 = dictPrice['sell5']
        self.sell5volume =dictPrice['sell5volume']
        self.date = dictPrice['date']
        self.time = dictPrice['time']
        self.retain = ''

    def GetName(self):
        if rh:
            namekey = self.code+'name'
            nameStr=rh.get(namekey)
            if nameStr == None:
                if (debug): print(type(nameStr), nameStr)
                return 'None'
            return sat_util.ToUTF8(nameStr)
        else:
            return "none"

    def PricePrint(self):
        #print('*******************************')
        print(': 名称  :  ', self.GetName(),  ': 代码  :', self.code) # 代码，应该不需要包含sz,sh,hk
        print(': 当前价格 :', self.cur,': 昨收  :', self.closed, ': 今开  :', self.opening)
        print(': 涨跌  :', self.updown, ': 涨跌%  :', self.updownrate, ': 最高  :', self.highest, ': 最低  :', self.lowest)
        print(': 成交量（手）  :', self.volume, ': 成交额（万）  :', self.turnover, ': 外盘  :', self.outdisk, ': 内盘  :', self.indisk) 
        print(': 换手率  :', self.turnoverrate, ': 市盈率  :', self.earningsrate, ': 市净率  :', self.pb)
        print(': 最高  :', self.highest, ': 最低  :', self.lowest, ': 振幅  :', self.amplitude)
        print(': 涨停价  :', self.uplimit, ': 跌停价  :', self.downlimit) 
        print(': 买一~~买五: ', self.buy1, self.buy2, self.buy3, self.buy4, self.buy5, )
        print(': 买一~~买五量: ', self.buy1volume, self.buy2volume, self.buy3volume, self.buy4volume, self.buy5volume)
        print(': 卖一~~卖五: ', self.sell1, self.sell2, self.sell3, self.sell4, self.sell5)
        print(': 卖一~~卖五量: ', self.sell1volume, self.sell2volume, self.sell3volume, self.sell4volume, self.sell5volume)
        print(': 时间  :', self.date, self.time)
        #print('date and time is :', dateandtime)  
        print('*******************************')     #Transactionprice Items EscrowShares CirculationShares ,F001,F002,F003,F004,
    
    def NameCodeCurUpdown(self):
        #print('名称  代码  当前价  涨跌  涨跌幅% ')
        print(self.GetName(),' ', self.code, ' ', self.cur, ' ', self.updown, ' ', self.updownrate) 

    def PartW2CSV(self, f):
        try:
            l = [self.code, self.cur, self.volume, self.updown,self.updownrate,self.turnoverrate]
            print(','.join(l), file=f)
        except IOError:
            print("write file  RealTimePrice.csv failed.")
            print("Error: {}".format(err.msg))

    def AllW2CSV(self, f):
        try:
            l = [self.code, self.cur,self.updown, self.updownrate, self.highest,self.lowest, self.closed,self.opening, self.volume, self.turnover, self.turnoverrate, self.outdisk, self.indisk,self.earningsrate,self.pb, self.amplitude,self.uplimit, self.downlimit,self.buy1, self.buy1volume, self.buy2,self.buy2volume, self.buy3, self.buy3volume, self.buy4, self.buy4volume, self.buy5, self.buy5volume,self.sell1, self.sell1volume,self.sell2,self.sell2volume,self.sell3, self.sell3volume, self.sell4,self.sell4volume,self.sell5,self.sell5volume,self.date, self.time]
            print(','.join(l), file=f)
        except IOError:
            print("write file  ???.csv failed.")
            print("Error: {}".format(err.msg))

    def AllW2Mysql(self):  
        inHead = "insert into t_rt_price(code, cur,updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, downlimit,buy1, buy1volume, buy2,buy2volume, buy3, buy3volume, buy4, buy4volume, buy5, buy5volume,sell1, sell1volume,sell2,sell2volume,sell3, sell3volume, sell4,sell4volume,sell5,sell5volume,date,time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        l = [self.code, self.cur,self.updown, self.updownrate, self.highest,self.lowest, self.closed,self.opening, self.volume, self.turnover, self.turnoverrate, self.outdisk, self.indisk,self.earningsrate,self.pb, self.amplitude,self.uplimit, self.downlimit,self.buy1, self.buy1volume, self.buy2,self.buy2volume, self.buy3, self.buy3volume, self.buy4, self.buy4volume, self.buy5, self.buy5volume,self.sell1, self.sell1volume,self.sell2,self.sell2volume,self.sell3, self.sell3volume, self.sell4,self.sell4volume,self.sell5,self.sell5volume,self.date, self.time]
        print("mysql ", self.code)
            
        #self.code=str(self.code)
        ###dt=str(dt)
        #print(dt)
        #mydate= dt.isoformat()
        #mytime=  dt.isoformat()#datetime.time(1, 58, 59).isoformat()
        ##mydate=str(mydate)[0:10]
        #mydate=self.date
        #mytime=self.time
        ##mydate.strftime('%Y-%m-%d')
        ##mytime.strftime('%H:%M:%S')
        #print(type(mydate), mydate,'  ', type(mytime), mytime, type(self.time), self.time)
        #inHead = "insert into t_xxx(code,mydate,mytime) values(%s,%s,%s)"
        #l= [self.code, mydate, mytime]
        if (debug): 
            print("insert one data to mysql")
        sat_cmysql.Insert(inHead, l)

    def AllW2MysqlHistory(self):  
        inHead = "insert into t_h_price(code, cur, updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, downlimit,buy1,sell1,date,time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        l = [self.code, self.cur,self.updown, self.updownrate, self.highest,self.lowest, self.closed,self.opening, self.volume, self.turnover, self.turnoverrate, self.outdisk, self.indisk,self.earningsrate,self.pb, self.amplitude,self.uplimit, self.downlimit,self.buy1, self.sell1,self.date, self.time]
        print("mysql history ", self.code)
        if (debug): 
            print("insert one data to mysql history")
        sat_cmysql.Insert(inHead, l)
  
    def AllW2Redis(self):
        #key = rp.code+columns, 对于这样的安排是为了快速统计值的变化，还有一个原因是redis不支持对象存储(其它nosql也是不支持的，也可以自己写个TODO)
        if (str(r.lindex(self.code+'time', 0))[2:8] == self.time) and (str(r.lindex(self.code+'date', 0))[2:10] == self.date):
            if (debug): print("dup data")
            return None
        else:
            if (debug): print("insert data", type(r.lindex(self.code +'time', 0)),r.lindex(self.code+'time', 0), type(self.time))
        r.lpush(self.code+'cur', self.cur)
        r.lpush(self.code+'updown', self.updown)
        r.lpush(self.code+'updownrate', self.updownrate)
        r.lpush(self.code+'highest', self.highest)
        r.lpush(self.code+'lowest', self.lowest)
        r.lpush(self.code+'closed', self.closed)
        r.lpush(self.code+'opening', self.opening)
        r.lpush(self.code+'volume', self.volume)
        r.lpush(self.code+'turnover', self.turnover)
        r.lpush(self.code+'turnoverrate', self.turnoverrate) 
        r.lpush(self.code+'amplitude', self.amplitude)
        r.lpush(self.code+'earningsrate', self.earningsrate)
        r.lpush(self.code+'pb', self.pb)
        r.lpush(self.code+'uplimit', self.uplimit) 
        r.lpush(self.code+'downlimit', self.downlimit) 
        r.lpush(self.code+'outdisk', self.outdisk)
        r.lpush(self.code+'indisk', self.indisk) 
        r.lpush(self.code+'buy1', self.buy1)
        r.lpush(self.code+'buy2', self.buy2)
        r.lpush(self.code+'buy3', self.buy3) 
        r.lpush(self.code+'buy4', self.buy4) 
        r.lpush(self.code+'buy5', self.buy5)
        r.lpush(self.code+'buy1volume', self.buy1volume)
        r.lpush(self.code+'buy2volume', self.buy2volume) 
        r.lpush(self.code+'buy3volume', self.buy3volume)
        r.lpush(self.code+'buy4volume', self.buy4volume) 
        r.lpush(self.code+'buy5volume', self.buy5volume)
        r.lpush(self.code+'sell1', self.sell1)
        r.lpush(self.code+'sell2', self.sell2) 
        r.lpush(self.code+'sell3', self.sell3) 
        r.lpush(self.code+'sell4', self.sell4) 
        r.lpush(self.code+'sell5', self.sell5)
        r.lpush(self.code+'sell1volume', self.sell1volume)
        r.lpush(self.code+'sell2volume', self.sell2volume) 
        r.lpush(self.code+'sell3volume', self.sell3volume)
        r.lpush(self.code+'sell4volume', self.sell4volume) 
        r.lpush(self.code+'sell5volume', self.sell5volume)
        r.lpush(self.code+'date', self.date) # 可以优化，只是保存一次
        r.lpush(self.code+'time', self.time)
        #r.lpush(self.code+'tradeprice', self.tradeprice) 
        #r.lpush(self.code+'tradevolume', self.tradevolume) 
        #r.lpush(self.code+'tradeturnover', self.tradeturnover)
        #r.lpush(self.code+'recentytransaction', self.recentytransaction)
        if (debug): print(self.date, '  ', self.time)
        if (debug): print('rlen: ', r.llen(self.code+'cur'))
        if (debug): print('reids index ', r.lindex(self.code+'cur', 0))
        #r.lpop(self.code)

    def AllW2RedisHistory(self):
        #if (str(r.lindex(self.code+'time', 0))[2:8] == self.time) and (str(r.lindex(self.code+'date', 0))[2:10] == self.date):
        #    if (debug): print("dup data")
        #    return None
        #else:
        #    if (debug): print("insert data", type(r.lindex(self.code +'time', 0)),r.lindex(self.code+'time', 0), type(self.time))
        rh.lpush(self.code+'cur', self.cur)
        rh.lpush(self.code+'date', self.date) # 可以优化，只是保存一次
        #rh.lpush(self.code+'updown', self.updown)
        #rh.lpush(self.code+'updownrate', self.updownrate)
        rh.lpush(self.code+'highest', self.highest)
        rh.lpush(self.code+'lowest', self.lowest)
        rh.lpush(self.code+'closed', self.closed)
        rh.lpush(self.code+'opening', self.opening)
        rh.lpush(self.code+'volume', self.volume)
        #r.lpush(self.code+'turnover', self.turnover)
        #r.lpush(self.code+'turnoverrate', self.turnoverrate) 
        #r.lpush(self.code+'amplitude', self.amplitude)
        #r.lpush(self.code+'earningsrate', self.earningsrate)
        #r.lpush(self.code+'pb', self.pb)
        #r.lpush(self.code+'uplimit', self.uplimit) 
        #r.lpush(self.code+'downlimit', self.downlimit) 
        #r.lpush(self.code+'outdisk', self.outdisk)
        #r.lpush(self.code+'indisk', self.indisk) 
        #r.lpush(self.code+'buy1', self.buy1)
        #r.lpush(self.code+'sell1', self.sell1)
        #r.lpush(self.code+'time', self.time)
        if (debug): print('rlen: ', r.llen(self.code+'cur'))
        if (debug): print('reids index ', r.lindex(self.code+'cur', 0))


"""
得到RtPrice对象的函数接口
"""
def GetPrice(code):
    b, d = sat_down.Down(code)
    if b: 
        rp = RtPrice(d)
        if (debug): rp.PricePrint()
        return True, rp
    if(debug): print('GetPrice', len(d))
    return False, 'NULL'

def GetPriceMulti(codes):
    ldict = sat_down.DownMulti(codes)
    lrp=[]
    for i in range(0, len(ldict)):
        if len(ldict[i]) > 39:
            lrp.append(RtPrice(ldict[i]))
            if (debug): lrp[i].PricePrint()
    return lrp
    
"""
以下为测试用例
"""
def TestMysql():
    dp = {}
    dt=datetime.datetime.now()
    dp['code']='000003'
    dp['date']=str(dt)[0:10]
    dp['time']= str(dt)[11:19]
    dp['cur']='10.42'
    dp['updown'] = '1.0'
    dp['updownrate'] = '1.0' 
    dp['highest'] = '1.0'
    dp['lowest'] = '1.0'
    dp['closed'] = '1.0'
    dp['opening'] = '1.0'
    dp['volume'] = '1.0'
    dp['turnover'] = '1.0'
    dp['turnoverrate'] = '1.0'
    dp['outdisk'] = '1.0'
    dp['indisk'] = '1.0'
    dp['earningsrate'] = '1.0'
    dp['pb'] = '1.0' 
    dp['amplitude'] = '1.0' 
    dp['uplimit'] = '1.0' 
    dp['downlimit'] = '1.0'
    dp['buy1'] = '1.0'
    dp['buy1volume'] = '1.0'
    dp['buy2'] = '1.0'
    dp['buy2volume'] = '1.0'
    dp['buy3'] = '1.0'
    dp['buy3volume'] = '1.0'
    dp['buy4'] = '1.0'
    dp['buy4volume'] = '1.0'
    dp['buy5'] = '1.0'
    dp['buy5volume'] = '1.0'
    dp['sell1'] = '1.0'
    dp['sell1volume'] = '1.0'
    dp['sell2'] = '1.0'
    dp['sell2volume'] = '1.0'
    dp['sell3'] = '1.0'
    dp['sell3volume'] = '1.0'
    dp['sell4'] = '1.0'
    dp['sell4volume'] = '1.0'
    dp['sell5'] = '1.0'
    dp['sell5volume'] = '1.0'
    rp=RtPrice(dp)
    #rp.PricePrint()
    f=open(partfile, 'a')
    rp.PartW2CSV(f)
    f.close()
    f=open(alltest, "a")
    rp.AllW2CSV(f)
    print("write mysql")
    rp.AllW2Mysql()
    print("end")

def TestMysqlRealData():
    codes = ['601398','000001','000002']#,'601818'
    for i in range(0, len(codes)):
        b, rp = GetPrice(codes[i])
        if b: rp.AllW2Mysql()
    print("end TestMysql from qt")

def TestRedis():
    if not r.ping():
        print('error r no con!\n')
    codes = ['601388']#,'601398','601818'
    for i in range(0, len(codes)):
        b,rp = GetPrice(codes[i])
        if b: 
            rp.AllW2Redis()
            if (debug) : rp.PricePrint()
    
    print('this pop ', r.lindex(codes[0], 5))
    #print(r.delete(codes[0]+'1'))

def TestRedisMulti():
    if not r.ping():
        print('error r no con!\n')
    codes = ['002014', '000929', '600336', '600361', '002596', '600078', '600851', '002226', '000032', '600770', '000011', '000421', '002024', '600790', '002097', '600668', '002259', '000785', '600386', '601933', '600429', '600881', '000972', '600127', '002202', '600510', '600861', '600737', '000636', '000037', '600330', '600734', '002678', '600327', '002199', '600206', '002064', '002220', '600132', '601996', '601798', '600589', '600719', '000088', '600532', '002042', '600333', '002430', '600210', '600328', '600403', '600831', '002386', '600819', '600748', '000599', '002355', '601388', '000620', '600651', '600644', '000736', '600616', '000899', '002643', '002406', '000916', '600866']
    lrp=GetPriceMulti(codes)
    if (debug) : print('redis multi lrp', len(lrp))
    for i in range(0, len(lrp)):
        #lrp[i].AllW2Redis()
        lrp[i].PricePrint()
    print('end test redis multi')

if __name__ == '__main__':
    start = time.time()
    #TestMysql()
    #TestMysqlRealData()
    #TestRedis()
    TestRedisMulti()
    end = time.time()
    print("ms %d" %(end - start))


