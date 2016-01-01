#!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

# sat_algo_ta.py
# 基础技术分析算法

import time
import sat_ta
import sat_dbop

from sat_algo_public import *
from sat_algo_random import *

dAlgoParams = {}
#dAlgoParams = sat_dbop.RAllAlgoParams()

debug = False
#debug = True

#处理数据
def GetSrcDataByIndi(code, indi, queryN=-1):
    lret=[]
    #print('start', indi)
    if indi == None:
        print('indi empty')
        return lret
    elif (indi == 'macd' or indi=='rsi' or indi=='rsi2' or indi=='roc' or indi=='boll' or indi=='bbi' or indi=='bias' or indi=='ema'):
        b, u = sat_ta.GetDataByCodeIndi(code,'cur', queryN)
        if (debug): print('get data', b, indi)
        if b:
            lret.append(u)
    elif (indi=='wr' or indi=='cci' or indi=='kdj' or indi=='sar' or indi=='dmi' or indi=='shortHL'):
        b, c,h,l = sat_ta.GetCHLDataByCode(code, queryN)
        if (debug): print('get data', b, indi)
        if b:
            lret.append(c)
            lret.append(h)
            lret.append(l)
    elif indi == 'outside':
        #print('here')
        b, c,h,l = sat_ta.GetCHLDataByCode(code, queryN)
        b1, o = sat_ta.GetDataByCodeIndi(code, 'opening', queryN)
        #print('get data ....', b, b1, indi, o)
        if b and b1:
            lret.append(c)
            lret.append(h)
            lret.append(l)
            lret.append(o)
    elif (indi == 'vol'):
        #b, c = sat_ta.GetDataByCodeIndi(code,'cur', queryN)
        b, v = sat_ta.GetDataByCodeIndi(code,'volume', queryN)
        if (debug): print('get data', b, indi)
        if b:
            lret.append(v)
    else:
        print('indi error', indi)
    return lret

def GetJudgeDataPublic(algoName, lparams, ldata):
    judgeDataFunc = dBasicAlgo.get(algoName+'JudgeData')
    if None == judgeDataFunc or (0 == len(ldata)):
        print('no register algo, calc func or ldata is none', algoName, len(ldata))
        return False, None
    if (0 == len(lparams)):
        lparams = dBasicAlgo.get(algoName+'Params')

    #获取该技术指标的返回值，作为参数传入
    #print(algoName, judgeDataFunc)
    return  judgeDataFunc(ldata, lparams)
   
def GetAlgoFunc(algoName):
    algoFunc = dBasicAlgo.get(algoName)
    if None == algoFunc:
        print('no register algo func', algoName) 
        return False, None
    return True, algoFunc
    
def GetAlgoRet(code, algoName, ljudgeData):
    if debug : print(algoName, code, 'judge data len', len(ljudgeData))
    #print('judge', ljudgeData)
    arv = SAT_AlgoRV(code, algoName, ljudgeData)
    b, algoFunc = GetAlgoFunc(algoName)
    if (not b) or (0 == len(ljudgeData)):
        print('judgeData is none', code, algoName) 
        return False, arv
    #print('getAlgoRet', algoFunc)
    algoFunc(arv)
    return True, arv

def PublicTestAlgo(code, algoName, lparams=[], ldata=[]):
    if 0 == len(ldata):
        ldata=GetSrcDataByIndi(code, algoName)
    ljudgeData = GetJudgeDataPublic(algoName, lparams, ldata)
    return GetAlgoRet(code, algoName, ljudgeData)



"""
短期最高点：以收盘价做曲线，同时高于前一天收盘价和后一天收盘价的点;
短期最低点：以收盘价做曲线，同时低于前一天收盘价和后一天收盘价的点。
中期最高点：以所有短期最高点做曲线，同时高于临近的两个收盘价的点;
中期最低点：以所有短期最低点做曲线，同时低于临近的两个收盘价的点。
长期最高点：以所有中期最高点做曲线，同时高于临近的两个收盘价的点;
长期最低点：以所有中期最低点做曲线，同时低于临近的两个收盘价的点。
"""
def JudgeHL(arv,c,lH,lL):
    if 3 > len(lH) and 3 > len(lL):
        return None
    Ld0,Lc0=lL[0]
    Ld1,Lc1=lL[1]
    Ld2,Lc2=lL[2]

    Hd0,Hc0=lL[0]
    Hd1,Hc1=lL[1]
    Hd2,Hc2=lL[2]

    if (Hd1 - Hd0 < 4 and Hd2 - Hd1 < 4):
        if (Hc1 > Hc0 and Hc1 > Hc2):
            if (Hd0 == 1):
                arv.chance = 'sell'
    elif (Ld1 - Ld0 < 4 and Ld2 - Ld1 < 4):
        if (Lc1 < Lc0 and Lc1 < Lc2):
            if (Ld0 == 1):
                arv.chance = 'buy'
    else:
        arv.chance = 'wait'

#judge Data default first return value is bool type
def GetJudgeDataShortHL(lsrcData, args):
    c = lsrcData[0]
    b,lH,lL = sat_ta.ArrHL(c)
    if (b):
        return True,c,lH,lL

    return False,None,None,None

def AlgoShortHL(arv):
    b = arv.ljudgeData[0]
    #print('shortHL judgeData', arv.ljudgeData)
    if b:
        b,c,lH,lL= arv.ljudgeData[0], arv.ljudgeData[1], arv.ljudgeData[2], arv.ljudgeData[3] 
        if b:
            #judge algo
            JudgeHL(arv, c,lH,lL)

def TestAlgoShortHL(code, ldata):
    args= []
    return PublicTestAlgo(code, 'shortHL', args, ldata)


def JudgeOutside(arv,c,h,l,o):
    if c.size < 2:
        return 
    if c[1] < o[1] and  c[0] > o[0] and c[1] > o[0] and o[1] < c[0] and h[0] > h[1] and l[0] < l[1]:
#    if h[0] > h[1] and l[0] < l[1] and c[0] > o[0] and c[1] < o[1] and c[1] :
        arv.chance = 'buy'
    else:
        arv.chance = 'wait'

def GetJudgeDataOutside(lsrcData, args):
    return True, lsrcData[0], lsrcData[1], lsrcData[2],lsrcData[3]

def AlgoOutside(arv):
    if 3 <= len(arv.ljudgeData):
        b,c,h,l,o=arv.ljudgeData[0], arv.ljudgeData[1], arv.ljudgeData[2], arv.ljudgeData[3],arv.ljudgeData[4]
        #judge algo
        if b:
            JudgeOutside(arv, c,h,l,o)


def TestAlgoOutside(code, ldata):
    args=[]
    return PublicTestAlgo(code, 'outside', args, ldata)


"""
VOLUME线　画法：若今日收市价高过昨日收市价，成交量画红色空心实体；否则画绿色实心。
MA1、MA2、MA3分别为成交量的M1日、M2日、M3日均线
参数：M1、M2、M3一般取5日、10日、20日
"""    
#VOL
def JudgeVOL(arv,lv,lma1,lma2,lma3):
    if(debug): print('judge vol', lv[0], lma1[0],lma2[0],lma3[0])
    if lv.size < 2 and lma1.size < 2:
        return
    if (lv[0] > lma1[0]) and (lv[1] > lma1[1]) and (lv[2] > lma1[2]):
        arv.chance = 'buy'
    elif (lv[0] < lma1[0] and lv[1] < lma1[1] and lv[2] < lma1[2]):
        arv.chance = 'sell'
    else:
        arv.chance = 'wait'

def GetJudgeDataVOL(lsrcData, args):
    v = lsrcData[0]
    lret=[False, v]
    if len(args) != 3:
        print('vol args error')
        return lret
    b1,lma1=sat_ta.ArrVOL(v, args[0])
    b2,lma2=sat_ta.ArrVOL(v, args[1])
    b3,lma3=sat_ta.ArrVOL(v, args[2])
    if b1 and b2 and b3:
        lret.append(lma1)
        lret.append(lma2)
        lret.append(lma3)
        lret[0] = True
    return lret

def AlgoVOL(arv):
    lret=arv.ljudgeData
    #judge algo
    if 4 < len(lret):
        b,lv,lma1,lma2,lma3=lret[0],lret[1],lret[2],lret[3],lret[4]
        if b:
            JudgeVOL(arv, lv, lma1,lma2,lma3)


def TestAlgoVOL(code, ldata, N1=5,N2=10,N3=20):
    lparams=[N1,N2,N3]
    return PublicTestAlgo(code, 'vol', lparams, ldata)


"""
1. MACD 金叉：DIFF 由下向上突破 DEA,为买入信号。
2. MACD 死叉：DIFF 由上向下突破 DEA,为卖出信号。
3. MACD 绿转红：MACD 值由负变正,市场由空头转为多头。
4. MACD 红转绿：MACD 值由正变负,市场由多头转为空头。
5. DIFF 与 DEA 均为正值,即都在零轴线以上时,大势属多头市场,DIFF 向上突破 DEA,可作买。
6. DIFF 与 DEA 均为负值,即都在零轴线以下时,大势属空头市场,DIFF 向下跌破 DEA,可作卖。
#以下判断在混合指标算法集中体现
7. 当 DEA 线与 K 线趋势发生背离时为反转信号。
8. DEA 在盘整局面时失误率较高,但如果配合 RSI 及 KD 指标可适当弥补缺点。
#当MACD从负数转向正数，是买的信号。当MACD从正数转向负数，是卖的信号。
"""
def JudgeMACD(arv,lmacd,ldif,ldea):
    """ changed by jugl 2015-0103, need to test
    #code=arv.getCurCode()
    if (lmacd[1] < 0.0 and lmacd[0] > 0.0):
        arv.chance='buy'
    #elif (ldif[0] > 0 and ldea[0] > 0):
    #    arv.chance='buy'
    elif (lmacd[1] > 0.0 and lmacd[0] < 0.0):
        arv.chance = 'sell'
    #elif (ldif[0] < 0.0 and ldea[0] < 0.0):
    #    arv.chance='sell'
    elif (lmacd[0]-lmacd[1] > 0.1 or lmacd[1] - lmacd[0] > 0.1):
        arv.chance= 'notice'
    else:
        arv.chance='wait'
    """
    """
    if (lmacd[0] > 0.0 and lmacd[1] < 0.0 and abs(ldif[0]) < 0.1):
        arv.chance = 'buy'
    elif (lmacd[1] > 0.0 and lmacd[0] < 0.0 and abs(ldif[0]) > 0.15):
        arv.chance = 'sell'
    else:
        arv.chance = 'wait'
    """

    '''
    http://wenku.baidu.com/view/ec5026d1240c844769eaee32.html?re=view
    1．ADX指示行情处于盘整时，不采用该指标。
    2．对短线客来说，使用该指标时，可将日线图转变为小时图或者周期更短的图形。
    3．若要修改该指标的参数，不论放大或缩小参数，都应尽量设定为原始参数的整数倍。
    '''
    if (ldea[1] > 0 and ldif[1] > 0): # 多头市场
        if (ldea[0] > ldea[1] and ldif[0] > ldif[1]):
            arv.chance = 'buy'
        elif (ldea[0] < ldea[1] and ldif[0] < ldif[1]):
            arv.chance = 'sell' # or 'wait'
        elif (lmacd[1] < 0 and lmacd[1] > 0):
            arv.chance = 'buy' # '强势黄金交叉'
        elif (lmacd[1] > 0 and lmacd[0] < 0):
            arv.chance = 'sell' # '弱势死亡交叉'
        else:
            arv.chance = 'wait'
    elif (ldea[0] < 0 and ldif[0] < 0): # 空头市场
        if (ldea[0] < ldea[1] and ldif[0] < ldif[1]):
            arv.chance = 'sell'
        elif (ldea[0] > ldea[1] and ldif[0] > ldif[1]):
            arv.chance = 'buy' # or 'wait'
        elif (lmacd[1] < 0 and lmacd[0] > 0):
            arv.chance = 'buy' # ’弱势黄金交叉‘
        elif (lmacd[1] > 0 and lmacd[0] < 0):
            arv.chance = 'sell' # '强势死亡交叉'
        else:
            arv.chance = 'wait'
    else:
        arv.chance = 'wait'


def GetJudgeDataMACD(lsrcData, args):
    u = lsrcData[0]
    lret=[]
    if len(args) != 3:
        print('macd args error')
        return lret
    b,lmacd,ldif,ldea=sat_ta.ArrMACD(u,args[0],args[1],args[2])
    if b:
        lret.append(True)
        lret.append(lmacd)
        lret.append(ldif)
        lret.append(ldea)
    else:
        lret.append(False)
    return lret


#统一用这种接口，不同的算法使用同一种接口，新算法需要满足这种形式。
#算法macd 选择满足macd条件的代码
def AlgoMACD(arv):
    lret=arv.ljudgeData
    #judge algo
    if 3 < len(lret):
        b,lmacd,ldif,ldea=lret[0],lret[1],lret[2],lret[3]
        if lmacd.size > 2 and ldif.size > 2 and ldea.size > 2:
            JudgeMACD(arv, lmacd,ldif,ldea)


def TestAlgoMACD(code, ldata, FastN=12,SlowN=26,M=9):
    args= [FastN,SlowN,M]
    return PublicTestAlgo(code, 'macd', args, ldata)

#EMA
def JudgeEMA(arv,lema1,lema2,lema3,lema4):
    if(debug): print('judge ema', lema1)
    if (lema1[0] > lema2[0] > lema3[0] > lema4[0]):
        arv.chance = 'buy'
    elif (lema1[0] < lema2[0] < lema3[0] < lema4[0]):
        arv.chance = 'sell'
    else:
        arv.chance = 'wait'

def GetJudgeDataEMA(lsrcData, args):
    c = lsrcData[0]
    lret=[]
    if len(args) != 4:
        print('ema args error')
        lret.append(False)
        return lret
    b1,lema1=sat_ta.ArrEMA(u,args[0])
    b2,lema2=sat_ta.ArrEMA(u,args[1])
    b3,lema3=sat_ta.ArrEMA(u,args[2])
    b4,lema4=sat_ta.ArrEMA(u,args[3])
    if b1 and b2 and b3 and b4:
        lret.append(True)
        lret.append(lema1)
        lret.append(lema2)
        lret.append(lema3)
        lret.append(lema4)
    return lret

def AlgoEMA(arv):
    lret=arv.ljudgeData
    #judge algo
    if 4 < len(lret):
        return None
    b,lema1,leam2,leam3,leam4=lret[0],lret[1],lret[2],lret[3],lret[4]
    if b:
        JudgeEMA(arv, lema1,leam2,leam3,leam4)


def TestAlgoEMA(code,ldata,N1=5,N2=10,N3=20,N4=60):
    args=[N1,N2,N3,N4]
    return PublicTestAlgo(code, 'ema', args, ldata)

"""
1、当+DI线同时在ADX线和ADXR线及-DI线以下（特别是在50线以下的位置时），说明市场处于弱市之中，股市向下运行的趋势还没有改变，股价可能还要下跌，投资者应持币观望或逢高卖出股票为主，不可轻易买入股票。这点是DMI指标研判的重点。
2、当+DI线和-DI线同处50以下时，如果+DI线快速向上突破-DI线，预示新的主力已进场，股价短期内将大涨。如果伴随大的成交量放出，更能确认行情将向上，投资者应迅速短线买入股票。
3、当+DI线从上向下突破-DI线（即-DI线从下向上突破+DI线）时，此时不论+DI和-DI处在什么位置都预示新的空头进场，股价将下跌，投资者应短线卖出股票或以持币观望为主。
4、当+DI线、-DI线、ADX线和ADXR线等四线同时在50线以下绞合在一起窄幅横向运动，说明市场处于波澜不兴，股价处于横向整理之中，此时投资者应以持币观望为主。
5、当+DI线、ADX线和ADXR线等三线同时在50线以下的位置，而此时三条线都快速向上发散，说明市场人气旺盛，股价处在上涨走势之中，投资者可逢低买入﹣或持股待涨。（这点中因为-DI线是下降方向线，其对上涨走势反应不灵，故不予以考虑）。
6、对于牛股来说，ADX在50以上向下转折，仅仅回落到40——60之间，随即再度掉头向上攀升，而且股价在此期间走出横盘整理的态势。随着ADX再度回升，股价向上再次大涨，这是股价拉升时的征兆。这种情况经常出现在一些大涨的牛股中，此时DMI指标只是提供一个向上大趋势即将来临的参考。在实际操作中，则必须结合均线系统和均量线及其他指标一起研判。
"""
#DMI
def JudgeDMI(arv,lpdi,lmdi,ladx,ladxr,ladxm,c):
    if ladx[0] < lpdi[0] or 20 <= ladxr[0] <= 25:
        arv.chance = 'invalid' # 所有指标都无效
    elif lpdi[1] < lmdi[1] and lpdi[0] > lmdi[0] and lpdi[0] < 40 and lmdi[0] < 40:
        arv.chance = 'buy'
    elif lpdi[1] < 40 and ladx[1] < 40 and ladxr[1] < 40 and lpdi[0] >= lpdi[1] and ladx[0] >= ladx[1] and ladxr[0] >= ladx[1]:
        arv.chance = 'buy'
    elif lpdi[1] > lmdi[1] and lpdi[0] < lmdi[0]:
        arv.chance = 'sell'
    #elif ladx[2] <= ladx[1] and ladx[1] > ladx[0] and ladx[1] > 70:
    #    arv.chance = 'notice'
    elif (ladx[1] > 70 and ladx[1] > ladx[0] and ladx[1] >= ladx[2]): # 行情发生反转
        if (c[2] > c[1] > c[0]):
            arv.chance = 'buy'
        elif (c[2] < c[1] < c[0]):
            arv.chance = 'sell'
        else:
            arv.chance = 'wait'
    else:
        arv.chance = 'wait'

def GetJudgeDataDMI(lsrcData, args):
    c,h,l = lsrcData[0],lsrcData[1],lsrcData[2]
    lret=[]
    if len(args) != 3:
        print('dmi args error')
        return lret
    b,lpdi,lmdi,ladx,ladxr,ladxm=sat_ta.ArrDMI(c,h,l,args[0],args[1],args[2])
    if b:
        lret.append(True)
        lret.append(lpdi)
        lret.append(lmdi)
        lret.append(ladx)
        lret.append(ladxr)
        lret.append(ladxm)
        lret.append(c)
    else:
        lret.append(False)
    return lret

def AlgoDMI(arv):
    lret=arv.ljudgeData
    #judge algo
    if 6 < len(lret):
        b,lpdi,lmdi,ladx,ladxr,ladxm=lret[0],lret[1],lret[2],lret[3],lret[4],lret[5]
        if b and (len(lpdi) > 0):
            JudgeDMI(arv, lpdi,lmdi,ladx,ladxr,ladxm,lret[6])


def TestAlgoDMI(code, ldata, N=14,M=6,M1=14):
    args= [N,M,M1]
    return PublicTestAlgo(code, 'dmi', args, ldata)

    
"""
1.股价位于BBI上方，视为多头市场。
2.股价位于BBI下方，视为空头市场。
3.下跌行情中，若当日收盘价跌破BBI曲线，表示多转空，为卖出信号。
4.上涨行情中，若当日收盘价升越BBI曲线，表示空转多，为买入信号。
5.上升回档时，BBI为支持线，可以发挥支撑作用。
6.下跌反弹时，BBI为压力线，可以发挥阻力作用。
"""        
#BBI
def JudgeBBI(arv,lc,lbbi):
    if(debug): print('judge bbi', lc[0], lbbi[0])
    if (lbbi[0] > 1 and lc[0] > lbbi[0]): #多头
        arv.chance = 'buy'
    elif (lbbi[0] > 1 and lc[0] < lbbi[0]): #空头
        arv.chance = 'sell'
    else:
        arv.chance = 'wait'

def GetJudgeDataBBI(lsrcData, args):
    u = lsrcData[0]
    lret=[False]
    if len(args) != 4:
        print('args error')
        return lret
    b,lbbi=sat_ta.ArrBBI(u,args[0],args[1],args[2],args[3])
    if b:
        lret[0]=True
        lret.append(u)
        lret.append(lbbi)
    return lret

def AlgoBBI(arv):
    lret=arv.ljudgeData
    #judge algo
    if 3 > len(lret):
        return None
    b,lc,lbbi=lret[0],lret[1],lret[2]
    if b and lc.size >= 1 and lbbi.size >= 1:
        JudgeBBI(arv, lc, lbbi)


def TestAlgoBBI(code,ldata, N1=3,N2=6,N3=12,N4=24):
    args=[N1,N2,N3,N4]
    return PublicTestAlgo(code, 'bbi', args, ldata)


"""
1.RSI值于0-100之间呈常态分配，当5日RSI值在80%以上时，股市呈超买现象，若出现Ｍ头，为卖出时机。当5日RSI值在20%以下时，股市呈超卖现象，若出现Ｗ底为买进时机。
2.RSI一般选用5天、9天、14天作为参考基期，基期越长越有趋势性-慢速RSI，基期越短越有敏感性-快速RSI，
#当快速RSI由下往上突破慢速RSI时，为买进时机。
#当快速RSI由上往下跌破慢速RSI时，为卖出时机。
1、当短期RSI>长期RSI时，市场则属于多头市场；
2、当短期RSI<长期RSI时，市场则属于空头市场；
3、当短期RSI线在低位向上突破长期RSI线,则是市场的买入信号；
4、当短期RSI线在高位向下突破长期RSI线，则是市场的卖出信号。
"""
#judge rsi
def JudgeRSI(arv, lrsi1,lrsi2,lrsi3):
    if lrsi1.size < 4:
        return None
    if (lrsi1[0] > 80 or (lrsi1[0] <= lrsi2[0] <= lrsi3[0] and lrsi1[1] > lrsi2[1] > lrsi3[1])):
        arv.chance = 'sell'
    elif (lrsi1[0] < 20 or (lrsi1[0] >= lrsi2[0] >= lrsi3[0] and lrsi1[1] < lrsi2[1] < lrsi3[1])):
        arv.chance = 'buy'
    else:
        arv.chance='wait'

def GetJudgeDataRSI(lsrcData, args):
    u = lsrcData[0]
    lret=[False]
    if u.size > 2:
        lu=sat_math.np.zeros(u.size-1)
        for j in range(0, u.size-1):
            lu[j]=u[j]-u[j+1]
        b1,lrsi1 = sat_ta.ArrRSI(lu, args[0])
        b2,lrsi2 = sat_ta.ArrRSI(lu, args[1])
        b3,lrsi3 = sat_ta.ArrRSI(lu, args[2])
        if b1 and b2 and b3:
            lret[0]=True
            lret.append(lrsi1)
            lret.append(lrsi2)
            lret.append(lrsi3)
    return lret
    

def AlgoRSI(arv):
    lret=arv.ljudgeData
    #judge algo
    if 3 < len(lret):
        b,lrsi1,lrsi2,lrsi3=lret[0],lret[1],lret[2],lret[3]
        if b:
            JudgeRSI(arv, lrsi1, lrsi2, lrsi3)

def TestAlgoRSI(code, ldata, N1=6,N2=12,N3=24):
    args=[N1,N2,N3]
    return PublicTestAlgo(code, 'rsi', args, ldata)


#WR
def JudgeWR(arv, lwr):
    #code=arv.getCurCode()
    #if (debug): print('lwr data', lwr[:30])
    # 2015-01-15 为什么增加判断，是因为只有见到代码已经开始涨的情况下，再买
    if lwr.size < 2:
        return None
    if (lwr[0] >= 70):
        arv.chance='buy'
    elif (lwr[0] <= 30):
        arv.chance='sell'
    else:
        arv.chance='wait'

def GetJudgeDataWR(lsrcData, args):
    c=lsrcData[0]
    h=lsrcData[1]
    l=lsrcData[2]
    lret=[False]
    b,lwr=sat_ta.ArrWR(c,h,l,args[0])
    if b:
        lret[0]=True
        lret.append(lwr)
    return lret
    
    
def AlgoWR(arv):
    lret=arv.ljudgeData
    if 1 < len(lret):
        b,lwr=lret[0],lret[1]
        if b:
            #judge algo
            JudgeWR(arv, lwr)

def TestAlgoWR(code, ldata, N=14):
    args=[N]
    return PublicTestAlgo(code, 'wr', args, ldata)

    
def TestAlgoWRMultiParam(code):
    dRet={}
    for i in range(2, 100):
        args=[i]
        ldata=GetSrcDataByIndi(code, 'wr')
        arv=SAT_AlgoRV(code, 'wr', AlgoWR, args, ldata)
        if arv.isBuy():
            dRet[code] = i
    print('dRet=', dRet)
    return dRet

#CCI
def JudgeCCI(arv, lcci):
    code=arv.getCurCode()
    if (lcci[0] >= 100):
        arv.chance='sell'
    elif (lcci[0] <= -100):
        arv.chance='buy'
    else:
        arv.chance='wait'
    
def GetJudgeDataCCI(lsrcData, args):
    c=lsrcData[0]
    h=lsrcData[1]
    l=lsrcData[2]
    lret=[False]
    b,lcci=sat_ta.ArrCCI(c,h,l, args[0])
    if b:
        lret[0]=True
        lret.append(lcci)
    return lret

#适用短期内暴涨暴跌的非常态行情    
def AlgoCCI(arv):
    lret=arv.ljudgeData
    #judge algo
    if 1 < len(lret):
        b,lcci=lret[0],lret[1]
        if b:
            JudgeCCI(arv, lcci)


def TestAlgoCCI(code, ldata, N=14):
    args=[N]
    return PublicTestAlgo(code, 'cci', args, ldata)

#ROC
"""
（1）当ROC由下向上穿过MAROC，即金叉出现时，发出买入信号；
（2）当ROC由上向下穿过MAROC，即死叉出现时，发出卖出信号；
（3）股价创新低，而ROC未同时创新低，即底背离现象出现时，发出买入信号；
（4）股价创新高，而ROC未同时创新高，即顶背离现象出现时，发出卖出信号；
（5）在大行情中，当ROC与MAROC齐头向上时，是强势持有信号；当ROC与MAROC齐头向下时，发出卖出信号。
1.ROC向下跌破零，卖出信号；ROC向上突破零，买入信号
2.股价创新高，ROC未配合上升，显示上涨动力减弱
3.股价创新低，ROC未配合下降，显示下跌动力减弱
4.股价与ROC从低位同时上升，短期反弹有望
5.股价与ROC从高位同时下降，警惕回落
"""
def JudgeROC(arv, lroc, lrocma):
    if (lroc[0] > lrocma[0] and lroc[0] > 0):
        arv.chance='buy'
    elif (lroc[0] < lrocma[0] and lroc[0] < 0):
        arv.chance='sell'
    elif (lroc[0] > lroc[1] and lrocma[0] > lrocma[1]):
        arv.chance='buy'
    elif (lroc[0] < lroc[1] and lrocma[0] < lrocma[1]):
        arv.chance='sell'
    else:
        arv.chance='wait'
    
def GetJudgeDataROC(lsrcData, args):
    u = lsrcData[0]
    broc,lroc=sat_ta.ArrROC(u, args[1])
    brocma,lrocma=sat_ta.ArrROCMA(u, args[1], args[0]) 
    if broc and brocma:
        lret=[True,lroc,lrocma]
        return lret
    return [False]
    
def AlgoROC(arv):
    lret=arv.ljudgeData
    #judge algo
    if 2 < len(lret):
        b, lroc,lrocma=lret[0],lret[1],lret[2]
        if b:
            JudgeROC(arv, lroc, lrocma)

def TestAlgoROC(code, ldata, FastN=6, SlowN=12):
    args=[FastN,SlowN]
    return PublicTestAlgo(code, 'roc', args, ldata)


#KDJ
"""
1.K与D值永远介于0到100之间。D大于70时，行情呈现超买现象。D小于30时，行情呈现超卖现象。
2.上涨趋势中，K值小于D值，K线向上突破D线时，为买进信号。下跌趋势中，K大于D，K线向下跌破D线时，为卖出信号。
3.KD指标不仅能反映出市场的超买超卖程度，还能通过交叉突破发出买卖信号。
4.KD指标不适于发行量小、交易不活跃的股票，但是KD指标对大盘和热门大盘股有极高准确性。
5.当随机指标与股价出现背离时，一般为转势的信号。
6.K值和D值上升或者下跌的速度减弱，倾斜度趋于平缓是短期转势的预警信号。
"""
def JudgeKDJ(arv, lk,ld,lj):
    #code=arv.getCurCode()
    if (ld[0] >= 80 or lj[0] > 100 or lk[0] >= 90):
        arv.chance = 'sell'
    elif (ld[0] <= 30 or lj[0] < 10 or lk[0] <= 20):
        arv.chance = 'buy'
    elif (ld[0] <= 20 and (ld[0] == lj[0] == lk[0]) and (ld[0] > ld[1])):
        arv.chance = 'buy'
    elif (ld[0] >= 70 and (ld[0] == lj[0] == lk[0])):
        arv.chance = 'sell'
    #elif ((lj[0] > lj[1]) and (ld[0] - lk[0] > 3 or ld[0] - lk[0] < -3)):
    #    arv.chance = 'buy'
    #elif ((lj[0] < lj[1]) and (ld[0] - lk[0] > 3 or ld[0] - lk[0] < -3)):
    #    arv.chance = 'sell'        
    else:
        arv.chance = 'wait'
"""
    if (ld[0] >= 80 or lj[0] > 100 or lk[0] >= 90):
        arv.chance='sell'
    elif (ld[0] <= 20 or lj[0] < 0 or lk[0] <= 10):
        arv.chance='buy'
    elif (lk[0] > ld[0] and lk[1] < ld[1]):
        arv.chance='buy'
    elif (lk[1] > ld[1] and lk[0] < ld[0]):
        arv.chance='sell'
    elif (ld[0] < 50 and lj[0] < 50 and lk[0] < 50):
        if (lj[2] < ld[2] and lk[2] < ld[2] and lj[0] > lj[1] > lj[2]):
            if (lj[0] > ld[0] and lk[0] > ld[0]):
                arv.chance = 'buy'
    elif (abs(ld[0] - 50) < 10 and abs(lj[0] - 50) < 10 and abs(lk[0] - 50) < 10):
        if (lj[2] < ld[2] and lk[2] < ld[2] and lj[0] > lj[1] > lj[2]):
            if (lj[0] > ld[0] and lk[0] > ld[0]):
                arv.chance = 'buy'
    elif (lj[2] > 80 and lk[2] > 80):
        if (lj[2] > ld[2] and lk[2] > ld[2] and lj[0] < lj[1] < lj[2]):
            if (lj[0] < ld[0] and lk[0] < ld[0]):
                arv.chance = 'sell'
    else:
        arv.chance = 'wait'
"""

def GetJudgeDataKDJ(lsrcData, args):
    c=lsrcData[0]
    h=lsrcData[1]
    l=lsrcData[2]
    lret=[False]
    if len(c) > args[0]:
        b,lk,ld,lj=sat_ta.ArrKDJ(c,h,l,args[0],args[1],args[2])
        if b:
            lret[0]=True
            lret.append(lk)
            lret.append(ld)
            lret.append(lj)
    return lret

def AlgoKDJ(arv):
    lret=arv.ljudgeData
    if 3 < len(lret):
        b,lk,ld,lj=lret[0],lret[1],lret[2],lret[3]
        if b and (len(lk) > 0):
            #judge algo
            JudgeKDJ(arv, lk,ld,lj)

def TestAlgoKDJ(code, ldata, N=9, M1=3,M2=3):
    args=[N,M1,M2]
    return PublicTestAlgo(code, 'kdj', args, ldata)



#BIAS
def JudgeBIAS(arv, lbias1,lbias2,lbias3):
    if (lbias1[0] >= 8 or lbias2[0] >= 10 or lbias3[0] >= 16):
        arv.chance='sell'
    elif (lbias1[0] <= -8 or lbias2[0] <= -10 or lbias3[0] <= -16):
        arv.chance='buy'
    else:
        arv.chance='wait'
    
def GetJudgeDataBIAS(lsrcData, args):
    c=lsrcData[0]
    lret=[False]
    b,lbias1,lbias2,lbias3=sat_ta.ArrBIAS(c, args[0], args[1], args[2])
    if b:
        lret[0]=True
        lret.append(lbias1)
        lret.append(lbias2)
        lret.append(lbias3)
    return lret

def AlgoBIAS(arv):
    lret=arv.ljudgeData
    #judge algo
    if 3 < len(lret):
        b,lbias1,lbias2,lbias3=lret[0],lret[1],lret[2],lret[3]
        if b:
            JudgeBIAS(arv, lbias1,lbias2,lbias3)


def TestAlgoBIAS(code, ldata, N1=6,N2=12,N3=24):
    args=[N1,N2,N3]
    return PublicTestAlgo(code, 'bias', args, ldata)


#BOLL
"""
1.当布林线的上、中、下轨线同时向上运行时，表明股价强势特征非常明显，股价短期内将继续上涨，投资者应坚决持股待涨或逢低买入。
2.当布林线的上、中、下轨线同时向下运行时，表明股价的弱势特征非常明显，股价短期内将继续下跌，投资者应坚决持币观望或逢高卖出。
3.当布林线的上轨线向下运行，而中轨线和下轨线却还在向上运行时，表明股价处于整理态势之中。如果股价是处于长期上升趋势时，则表明股价是上涨途中的强势整理，投资者可以持股观望或逢低短线买入；如果股价是处于长期下跌趋势时，则表明股价是下跌途中的弱势整理，投资者应以持币观望或逢高减仓为主。
4.布林线的上轨线向上运行，而中轨线和下轨线同时向下运行的可能性非常小，这里就不作研判。
5.当布林线的上、中、下轨线几乎同时处于水平方向横向运行时，则要看股价目前的走势处于什么样的情况下来判断。
TODO
"""
def JudgeBOLL(arv, lmid,lup,ldown):
    code=arv.getCurCode()
    if (lup[0] > lup[1] > lup[2] and lmid[0] > lmid[1] > lmid[2] and ldown[0] > ldown[1] > ldown[2]):
        arv.chance='buy'
    elif (lup[0] < lup[1] < lup[2] and lmid[0] < lmid[1] < lmid[2] and ldown[0] < ldown[1] < ldown[2]):
        arv.chance='sell'
    else:
        arv.chance='wait'

def GetJudgeDataBOLL(lsrcData, args):
    u = lsrcData[0]
    b,lmid,lup,ldown=sat_ta.ArrBOLL(u, args[0])
    if b:
        lret=[True,lmid,lup,ldown]
        return lret
    return [False]
    
def AlgoBOLL(arv):
    lret=arv.ljudgeData
    if 3 < len(lret):
        b,lmid,lup,ldown=lret[0],lret[1],lret[2],lret[3]
        #judge algo
        if b:
            JudgeBOLL(arv, lmid,lup,ldown)
    

def TestAlgoBOLL(code, ldata, N=14):
    args=[N]
    return PublicTestAlgo(code, 'boll', args, ldata)


#SAR
"""
1、当股票股价从SAR曲线下方开始向上突破SAR曲线时，为买入信号，预示着股价一轮上升行情可能展开，投资者应迅速及时地买进股票。
2、当股票股价向上突破SAR曲线后继续向上运动而SAR曲线也同时向上运动时，表明股价的上涨趋势已经形成，SAR曲线对股价构成强劲的支撑，投资者应坚决持股待涨或逢低加码买进股票。
3、当股票股价从SAR曲线上方开始向下突破SAR曲线时，为卖出信号，预示着股价一轮下跌行情可能展开，投资者应迅速及时地卖出股票。
4、当股票股价向下突破SAR曲线后继续向下运动而SAR曲线也同时向下运动，表明股价的下跌趋势已经形成，SAR曲线对股价构成巨大的压力，投资者应坚决持币观望或逢高减磅。
"""
def JudgeSAR(arv, lc, lsar):
    if lsar.size < 2:
        return
    if lc[0] > lsar[0] and lc[1] < lsar[1]:
        arv.chance = 'buy'
    elif lc[0] < lsar[0] and lc[1] > lsar[1]:
        arv.chance = 'sell'
    else:
        arv.chance = 'wait'
    

def GetJudgeDataSAR(lsrcData, args):
    c=lsrcData[0]
    h=lsrcData[1]
    l=lsrcData[2]
    lret=[False]
    if len(c) > args[0]:
        b,lsar=sat_ta.ArrSAR(c,h,l,args[0],args[1],args[2])
        if b:
            lret[0]=True
            lret.append(c)
            lret.append(lsar)
            if(debug):print('data sar', c.size, lsar.size)
    return lret

def AlgoSAR(arv):
    lret=arv.ljudgeData
    if 2 < len(lret):
        b,lc,lsar=lret[0],lret[1],lret[2]
        #judge algo
        if b and lsar.size > 1 and lc.size > 1:
            JudgeSAR(arv, lc,lsar)

def TestAlgoSAR(code, ldata, N=4, step=0.02, maxAF=0.2):
    args=[N,step, maxAF]
    return PublicTestAlgo(code, 'sar', args, ldata)

# 基础算法和其默认参数，当增加基础函数时，该字典必须添加
dBasicAlgo={'wr':AlgoWR, 'wrParams':[14], 'kdj':AlgoKDJ, 'kdjParams':[9,3,3], 'rsi':AlgoRSI, 'rsiParams':[6,12,24], 'macd':AlgoMACD, 'macdParams':[12,26,9],'bbi':AlgoBBI,'bbiParams':[3,6,12,24],'cci':AlgoCCI,'cciParams':[14],'roc':AlgoROC,'rocParams':[6,12],'boll':AlgoBOLL,'bollParams':[14],'sar':AlgoSAR,'sarParams':[4,0.02,0.2],'maParams':[5],'bias':AlgoBIAS,'biasParams':[6,12,24],'bias36':AlgoBIAS,'bias36Params':[36,36,36],'dmi':AlgoDMI,'dmiParams':[14,6,14],'vol':AlgoVOL,'volParams':[5,10,20],'shortHL':AlgoShortHL, 'shortHLParams':[], 'outside':AlgoOutside, 'outsideParams':[], 'wrJudgeData':GetJudgeDataWR,  'kdjJudgeData':GetJudgeDataKDJ, 'rsiJudgeData':GetJudgeDataRSI, 'macdJudgeData':GetJudgeDataMACD, 'bbiJudgeData':GetJudgeDataBBI, 'cciJudgeData':GetJudgeDataCCI, 'rocJudgeData':GetJudgeDataROC, 'bollJudgeData':GetJudgeDataBOLL, 'sarJudgeData':GetJudgeDataSAR, 'biasJudgeData':GetJudgeDataBIAS, 'dmiJudgeData':GetJudgeDataDMI, 'volJudgeData':GetJudgeDataVOL, 'shortHLJudgeData':GetJudgeDataShortHL, 'outsideJudgeData':GetJudgeDataOutside}
    

if __name__ == '__main__':
    start = time.time()
    c,qcodes=GetCodesBySingleKeyLimit('*cur', 2, 100)
    #codes=codes[0:2]
    print('codes num:', len(qcodes))
    lbuys=[]
    lsells=[]
    #qcodes =  ['600358', '002308', '000960', '600265', '002657', '600385', '000498', '002256', '002696', '002576', '600455', '002504', '002490', '000977', '002262', '002332', '000901', '002673', '600562', '600872', '000948', '002192', '600151', '002068', '600458', '002324', '000795', '600476', '603806', '600754', '600526', '600444', '601258', '000716', '000421', '600629', '600311', '000671', '601098', '603611', '601226', '600531', '000980', '601018', '200058', '002242', '600634', '002435', '600662', '002740', '000800']
    codes=[]
    for i in range(0, len(qcodes)):
        if '3' != qcodes[i][0]:
            codes.append(qcodes[i])
    for i in range(0, len(codes)):
#        ldata = GetSrcDataByIndi(codes[i], 'kdj')        
#        print('here')
        ldata = GetSrcDataByIndi(codes[i], 'outside')
#        b,arv = TestAlgoShortHL(codes[i], ldata)
#        b,arv = TestAlgoMACD(codes[i], ldata)
#        b,arv = TestAlgoRSI(codes[i], ldata)
#        b,arv = TestAlgoBBI(codes[i], ldata)
#        b,arv = TestAlgoCCI(codes[i], ldata)
#        b,arv = TestAlgoROC(codes[i], ldata)
#        b,arv = TestAlgoKDJ(codes[i], ldata)
#        b,arv = TestAlgoWR(codes[i], ldata)
#        b,arv = TestAlgoWR(codes[i], ldata, N=13)
#        b,arv = TestAlgoWR(codes[i], ldata, N=34)
#        b,arv = TestAlgoWR(codes[i], ldata, N=89)
#        b,arv = TestAlgoBOLL(codes[i], ldata)
#        b,arv = TestAlgoSAR(codes[i], ldata)
#        b,arv = TestAlgoShortHL(codes[i], ldata)
        b,arv = TestAlgoOutside(codes[i], ldata)
#        b,arv = TestAlgoBIAS(codes[i], ldata)
#        b,arv = TestAlgoDMI(codes[i], ldata)
#        b,arv = TestAlgoVOL(codes[i], ldata)
        if b:
            arv.saveBuySellCode(lbuys, lsells)
            if (debug): print('code, algoname,chance', codes[i], arv.indi, arv.chance)
    print('end sell codes',len(lsells), lsells)
    print('end buy codes', len(lbuys), lbuys)
    end = time.time()
    print("total seconds %d" %(end - start))

