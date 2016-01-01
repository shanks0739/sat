#!/usr/bin/env python3  
#coding=utf-8
# -*- coding:utf-8 -*-  


"""
golbal var
"""  
debug = False
#debug = True

import time
import datetime
import csv

import sat_util
import sat_thread
import sat_rtprice
import sat_down
import sat_credis
import sat_cmysql

r = sat_credis.r
rh = sat_credis.rh

codesfile = "util/A8.csv"
platefile = "util/plate.csv"
allhistory = "util/allhistory_sina.csv"


######################################################################
"""
thread op, public func
global var
"""
defaultStep = 5
defaultWorkNum = 30

def GetWorkNumStep(n):
    workNum = defaultWorkNum
    step = defaultStep
    if (n < step):
        workNum = 1
    elif (n < 2000):
        workNum = (n / step) + 1
    else:
        workNum = defaultWorkNum
    return workNum, step


def WorkOnce(func, codes):
    if (debug): print('WorkOnce', len(codes))
    n = len(codes)
    workNum,step=GetWorkNumStep(n)
    start = 0
    t = sat_thread.SAT_Threads(workNum, defaultStep)
    while True and start <= n:
        splitcodes=codes[start: start+step]
        t.add_job(func, splitcodes)
        start += step
    t.wait_allcomplete()
    if (debug): print('save to db end...' ' n= ', n, 'start = ', start)

def TimeCheck(h, m):
    if ((h == 9 and m >= 15) or (h>9 and h < 11) or (h == 11 and m <= 35) or (h >=13 and h<15) or (h == 15 and m <= 5)):
        return True
    return False
    

def WorkByTimeLimit(func, codes):
    n = len(codes)
    workNum,step=GetWorkNumStep(n)
    debug=True
    start = 0
    t = sat_thread.SAT_Threads(workNum, 1)
    c = 0
    taskNum = 0
    while True:
        h=int(time.strftime("%H"))
        m=int(time.strftime("%M"))
        if TimeCheck(h,m) and t.checkTaskEmpty(): #检测任务是否为空
            while True:
                splitcodes=codes[start: start+step]
                t.add_job(func, splitcodes)
                start += step
                if (start >= n): #本次任务加载完成
                    taskNum += 1
                    start = 0
                    print("restart join jobs ", taskNum)
                    break
        elif (h == 15 and m >= 10):
            print('not trading time, program exit', h)
            break
        elif (h > 15 or h < 8):
            print('not trading time, program exit', h)
            break
        
        time.sleep(0.1)
        c += 1
        #print("empty running or again get task")
    print("wait end...",'main count= ',c,  ' task num=', taskNum)
    t.wait_allcomplete()
    if (debug): print('Save2DBByTimeLimit end...' ' n= ', n, 'start = ', start)    


def WAll2DBOnce(func):
    codes=sat_util.GetAllCodesFromCSV()
    if (debug): print('WAllCodes2DBOnce', len(codes))
    WorkOnce(func, codes)

def WAll2DBByTime(func):
    codes=sat_util.GetAllCodesFromCSV()
    if (debug): print('WAllCodes2DBByTime', len(codes))
    WorkByTimeLimit(func, codes)

#######################################################################

"""
operate reids 
W 开头表示是写入数据到redis
R 开头表示是从redis读出数据
D 开头表示是删除redis的数据

"""
#插入名称到reids
def WName2Redis():
    c = csv.reader(open(codesfile, encoding='utf8'))
    for id, code, name in c:
        if code != 'NULL' and len(code) >= 6:
            #name=sat_util.ToGB(name)
            rh.set(code[:6]+'name', str(name))
            if (debug): print(code[:6], type(name), name)

#插入行业代码到redis history
def WPlate2Redis():
    p = csv.reader(open(platefile, encoding='utf16'))
    plates={}
    for plate, code, name in p:
        #insert redis
        rh.lpush(plate, code)
        plates[plate]=name
        #print(name)
    for i in plates:
        rh.lpush(i,plates[i])
        if (debug): print(i,plates[i])

#保存单个数据到redis
def WSingle2Redis(code):
    b,rp = sat_rtprice.GetPrice(code)
    if b: 
        rp.AllW2Redis()
        if (debug) : rp.PricePrint()
    if (debug): print("end or failed", b)

#保存多个数据到redis 一般使用这个接口
def WMulti2Redis(codes):
    lrp = sat_rtprice.GetPriceMulti(codes)
    for i in range(0, len(lrp)):
        lrp[i].AllW2Redis()
        if (debug): lrp[i].PricePrint()
    if (debug): print(len(lrp), ' end')

#保存一次所有实时数据到redis
def WAll2RedisOnce():
    WAll2DBOnce(WMulti2Redis)

#保存所有实时数据，并且按交易时间存入    
def WAll2RedisByTime():
    codes=sat_util.GetAllCodesFromCSV()
    if (debug): print('WAll2ReidsByTime', len(codes))
    WorkByTimeLimit(WMulti2Redis, codes)

#从CSV文件中读入数据到redis
#一般把csv文件中的数据导入到历史数据库
def W2RedisByCSV():
    hisSina='util/his_sina/his_sina.csv'
    f=open(hisSina, "r", encoding='utf-8')
    c = csv.reader(f)
    for code,date,o,h,cur,l,v in c:
        if code != 'NULL':
            rh.lpush(code[0:6]+'cur', cur)
            rh.lpush(code[0:6]+'date', date)
            rh.lpush(code[0:6]+'opening', o)
            rh.lpush(code[0:6]+'highest', h)
            rh.lpush(code[0:6]+'lowest', l)
            rh.lpush(code[0:6]+'volume', v)
    print("done sina csv")


   
#Read Redis
def RSingleNumFromRedis(code, indicator, n):
    ret = []
    lret = []
    if rh:
        if (n > 0):
            n = n - 1
        #数据是否重复，不应该由此处来判断，后面应该有个后台运行的程序来保证数据是一致，不重复的
        ret = rh.lrange(code+indicator, 0, n)
        if (debug): print('get data=', ret)
    for i in range(0, len(ret)):
        tmp=str(ret[i])
        tmp=float(tmp[2:len(tmp)-1])
        if (debug): print(type(tmp), tmp)
        #lret.insert(0, tmp) #倒序，时间上最新的数据放在列表最末尾
        lret.append(tmp)#应该把最新的放在列表最前面

    return lret

# read cur price
def RCurPriceFromRedis(codes):
    lret = []
    if r and rh:
        for i in range(0, len(codes)):
            ret = r.lrange(codes[i]+'cur', 0, 0) #取一个实时数据
            if len(ret) == 0:
                ret = rh.lrange(codes[i]+'cur', 0, 0)
            print('get data=', ret)
            if len(ret) == 0:
                lret.append(0.0)
            else:
                #print(str(ret[0])[2:-1])
                lret.append(float(str(ret[0])[2:-1]))
    return lret

def RSingleFromRedis(code, indicator, n):
    ret = []
    lret = []
    if rh:
        if (n > 0):
            n = n - 1
        ret = rh.lrange(code+indicator, 0, n)
        for i in range(0, len(ret)):
            lret.append(str(ret[i])[2:-1])
    return lret

def TestRedisRead():
    code='000001'
    indicator='cur'
    ret = RSingleNumFromRedis(code,indicator, 100)
    lret = RSingleFromRedis(code,'date',10)
    print('date', lret)
    print(ret)
    

#del keys from redis
def DKeysByCodesDate(codes):
    if not r or not rh:
        return False
    
    now = datetime.datetime.now()
    for i in range(0, len(codes)):
        ret = rh.lrange(codes[i]+'date', 0, 0)
        if (debug): print('key, ret=', codes[i]+'date', ret)
        strDate=str(ret)
        lenDate = len(strDate)
        if lenDate < 10:
            continue
        curDate = datetime.datetime.strptime(strDate[3:lenDate-2], '%Y%m%d')
        delta = now - curDate
        if (debug): print(now, curDate, delta)
        if delta.days >= 3: # TODO 不严谨
            lkeys=r.keys(codes[i]+'*')
            if(debug): print(lkeys)
            for j in range(0, len(lkeys)):
                #print(str(lkeys[j])[2:-1])
                r.delete(str(lkeys[j])[2:-1])
            #删除历史keys
            lkeys = rh.keys(codes[i]+'*')
            for j in range(0, len(lkeys)):
                rh.delete(str(lkeys[j])[2:-1])
                           
                
            
def TestDelKeys():
    codes=sat_util.GetAllCodesFromCSV()
    dcodes=codes
    print('del codes', dcodes)
    DKeysByCodesDate(dcodes)
    

"""
operate mysql
"""
def WSingle2Mysql(code):
    b, rp = sat_rtprice.GetPrice(code)
    if b:
        rp.AllW2Mysql()
        if (debug): rp.PricePrint()

lrpMysql=[]
def WMulti2Mysql(codes):
    lrp = sat_rtprice.GetPriceMulti(codes)
#    for i in range(0, len(lrp)):
#        lrp[i].AllW2Mysql()
#        if (debug): lrp[i].PricePrint()

    for i in range(0, len(lrp)):
        lrpMysql.append(lrp[i])
    #lrpMysql.extend(lrp)

#保存一次到mysql(t_rt_price, t_h_price, redis)
def WAll2MysqlRedisOnce():
    WAll2DBOnce(WMulti2Mysql)
    for i in range(0, len(lrpMysql)):
        lrpMysql[i].AllW2Mysql()
        # write history table t_h_price;
        lrpMysql[i].AllW2MysqlHistory()
    for i in range(0, len(lrpMysql)):
        # write redis 
        lrpMysql[i].AllW2RedisHistory()

#保存代码算法的参数到表中 lrangeData=std,avg,max,min
def WAlgoParams2Mysql(code,algoName, lparams, lrangeData):
    now = datetime.datetime.now()
    mydate = now.strftime('%Y%m%d')
    count = len(lparams)

    inHead = "replace into t_algo_params(code,algoname,date,pcount,p1,p2,p3,p4,p5,pstd,pavg,pMax,pMin) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    l = [code,algoName, mydate, str(count), '0', '0', '0', '0', '0', str(lrangeData[0]), str(lrangeData[1]), str(lrangeData[2]), str(lrangeData[3])]
    for i in range(0, count):
        l[i+4] = str(lparams[i])
    print("insert one params to mysql", inHead,l)
    sat_cmysql.Insert(inHead, l)
 
def TestWAlgoParams():
    lparams=[1.16534316463+3.11111111111]
    lrangeData=[1.16534316463,3.11111111111,5.0,2.0]
    codes=['600156']
    WAlgoParams2Mysql(codes[0], 'wr', lparams, lrangeData)
    
def RParamsByCodeAlgoName(code, algoName):
    defaultCond = 'code=000000' + ' and algoname=' + '\''+algoName+'\'' + ' order by date desc limit 1;'
    cond = 'code=' + code + ' and algoname=' + '\''+algoName+'\'' + ' order by date desc limit 1;'
    select_params = 'select date, p1,p2,p3,p4,p5 from t_algo_params where ' + cond
    select_default_params = 'select date, p1,p2,p3,p4,p5 from t_algo_params where ' + defaultCond
    if (debug): print(select_params)
    lret=[]
    sat_cmysql.Select(select_params)
    for (date,p1,p2,p3,p4,p5) in sat_cmysql.cursor:
        if (debug): print(code, algoName, date,p1,p2,p3,p4,p5)
        if (p1 == None):
            break
        lret.append(p1)
        lret.append(p2)
        lret.append(p3)
        lret.append(p4)
        lret.append(p5)
    if (0 == len(lret)):
        print('default params', select_default_params)
        sat_cmysql.Select(select_default_params)
        for (date,p1,p2,p3,p4,p5) in sat_cmysql.cursor:
            if (debug): print(code, algoName, date,p1,p2,p3,p4,p5)
            lret.append(p1)
            lret.append(p2)
            lret.append(p3)
            lret.append(p4)
            lret.append(p5)
    return lret
    
def TestRAlgoParams():
    code='000001'
    algoName = 'wr'
    lret=RParamsByCodeAlgoName(code, algoName)
    print('test read algo params end', lret)

def RAllAlgoParams():
    dRet={}
    select_params = 'select code, algoname, p1,p2,p3,p4,p5 from t_algo_params order by date;'
    if(debug): print(select_params)
    sat_cmysql.Select(select_params)
    for (code, algoname, p1,p2,p3,p4,p5) in sat_cmysql.cursor:
        lret=[]
        if (debug): print(code, algoname,p1,p2,p3,p4,p5)
        if (p1 == None):
            break
        lret.append(p1)
        lret.append(p2)
        lret.append(p3)
        lret.append(p4)
        lret.append(p5)
        #print(dRet.get(code+algoname), lret)
        if None == dRet.get(code+algoname):
            dRet[code+algoname]=lret
    return dRet


dAlgoParams={}
def TestRAllAlgoParams():
    dAlgoParams = RAllAlgoParams()
    print('test read all algo params', dAlgoParams)
    
"""
csv file
"""
def WAll2CSVOnce():
    f = open('RealTimePrice.csv', 'w', encoding='utf8')
    codes=sat_util.GetAllCodesFromCSV()
    for i in range(0, len(codes)):
        b, rp = sat_rtprice.GetPrice(code)
        if b:
            #rp.PricePrint()
            rp.WriteFile2CSV()
    f.close()

def WAll2CSVHistory():
    codes=sat_util.GetAllCodesFromCSV()
    qcodes=codes
    now = datetime.datetime.now()
    start= datetime.date(2014,1,1)
    hisSina = sat_util.CreateFileNameByDate("util/his_sina/his_sina_",now, start)
    f=open(hisSina, "w", encoding='utf-8')
    for i in range(0, len(qcodes)):
        sat_down.DownHistorySN(qcodes[i],now, start, f)

def WMulit2CSVHistory(codes):
    if (debug): print("len codes:",len(codes))
    now = datetime.datetime.now()
    start= datetime.date(2015,1,1)
    hisSina = sat_util.CreateFileNameByDate("util/his_sina/his_sina_"+codes[0]+'_',now, start)
    f=open(hisSina, "w", encoding='utf-8')
    for i in range(0, len(codes)):
        sat_down.DownHistorySN(codes[i],now, start, f)
        
#做一个多线程的下载
def WAll2CSVHistoryOnce():
    codes=sat_util.GetAllCodesFromCSV()
    qcodes=[]
    for i in range(0, len(codes)):
        qcodes.append(codes[i])
    if (debug): print('WAll2CSVHistoryOnce', len(qcodes))
    WorkOnce(WMulit2CSVHistory, qcodes)
        
"""
sat_rtprice test csv,mysql,redis start 
"""



if __name__ == '__main__':
    start = time.time()
    #WName2Redis()
    #Plate2Redis()
    WAll2MysqlRedisOnce()
    #WAll2RedisOnce()
    #WAll2RedisByTime()
    #TestRedisRead()
    #WAll2CSVHistory()
    #WAll2CSVHistoryOnce()
    #W2RedisByCSV()
    TestDelKeys()
    #TestWAlgoParams()
    #TestRAlgoParams()
    #TestRAllAlgoParams()
    end = time.time()
    print("total s %d" %(end - start))
    
