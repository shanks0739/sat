 #!/usr/bin/env python3  
# -*- coding:utf-8 -*-  

# sat_ta.py
# Technical indicators
# 技术指标 用于支持算法的基础指标
# 指标只是提供其算法过程，只是提供判断依据，在sat_algo中做判断

#股票十大常用指标类型
"""
1、大势型
包括：ABI、ADL、ADR、ARMS、BTI、C&A、COPPOCK、MCL、MSI、OBOS、TRIM、STIX、TBR。
钱龙软件将各种类型、专用于判断大盘的走势的指标归于此类，大势型指标一般无法在个股画面中使用(COPPOCK指标除外)。

2、超买超卖型 KDJ,WR KDJ+DMI+VOL
包括：CCI、DRF、KDJ、K%R、KAIRI、MFI、MOM、OSC、QIANLONG、ROC、RSI、SLOWKD、VDL、W%R、BIAS、BIAS36、布林极限、极限宽。
大约有五分之一的指标属于这种类型，完全精当地应用、解释，相当复杂，但只要掌握它的“天线”和“地线”的特征，各种难题就可以迎刃而解了。
天线和地线都于中轴线平行，天线位于中轴线上方、地线位于中轴线下方，两者离中轴线有相同的距离。天线可视为指标压力或是常态行情中的上涨极限。地线可视为指标支撑或常态行情中的下跌极限。这里的常态行情是指涨跌互见、走势波动以波浪理论的模式进行、并且促使指标持续上下波动与固定的范围里面的情形，连续急涨急跌或瞬间的暴涨暴跌都不能算是常态行情。

3、趋势型
包括：ASI、CHAIKIN、DMA、DMI、DPO、EMV、MACD、TRIX、终极指标、VHF、VPT、钱龙长线、钱龙短线、WVAD
本类型指标至少有两条线，指标以两条线交叉为信号：
趋向类指标的讯号发生，大致上都是以两条线的交叉为准，把握这个重点就可以运用自如。

4、能量型
包括：BRAR、CR、MAR、梅斯线、心理线、VCI、VR、MAD。
本类型指标是股价热度的温度计，专门测量股民情绪高亢或沮丧。
指标数据太高，代表高亢发烧；
指标数据太低，代表沮丧发冷；

5、成交量型
包括：ADVOL、成交值、负量指标、OBV、正量指标、PVT、成交量、SSL、邱氏量法、成本分布。
成交量型有N字波动型和O轴穿越型。信号发生的标志有：

6、均线型
包括：BBI、EXPMA、MA、VMA、HMA、LMA。
即各种不同算法的平均线。主要通过短期均线穿越长期均线的结果，判断是否为买卖信号。

7、图表型
包括：K线、美国线、压缩图、收盘价线、等量线、LOGB、LOGH、LOGK、等量K线、○×图、新三价线、宝塔线、新宝塔线。
是以K线为基础派生出来的价格图形，通过图形的特征形态及其组合，来判断买卖信号和预测涨跌。

8、选股型
包括：CSI、DX、PCNT%、TAPI、威力雷达、SV。
主要用途是用于筛选有投资价值股票的一类指标。

9、路径型
包括：布林线、ENVELOPE、MIKE、风林火山。
也称为压力支撑型。图形区分为上限带和下限带，上限代表压力，下限代表支撑。其指标图形特点是：股价向上触碰上限会回档；股价向下触碰下限会反弹；不同指标有特殊的不同含义。

10、停损型
包括：SAR、VTY。
此类指标不仅具备停损的作用而且具有反转交易的功能，所以，不能单纯以停损的观念看待这个指标，而是一个会产生交易信号的相对独立的交易系统。
股价上涨则停损圈圈（红色）位于股价下方；
股价下跌则停损圈圈（绿色）位于股价上方；
收盘价由下往上突破圈圈（绿色）为买进信号；
收盘价由上往下跌破圈圈（红色）为卖出信号。
"""

import time
import sat_dbop
#from sat_math import *
import sat_math

debug = False
#debug = True
"""
public fun
"""
def GetDataByCodeIndi(code, indicator='cur', N=-1):
    lret = sat_dbop.RSingleNumFromRedis(code, indicator, N)
    if (len(lret) > 0):
        return True, sat_math.List2npArray(lret)
    return False,None

def GetCHLDataByCode(code, N=-1):
    c = sat_dbop.RSingleNumFromRedis(code, 'cur', N)
    h = sat_dbop.RSingleNumFromRedis(code, 'highest', N)
    l = sat_dbop.RSingleNumFromRedis(code, 'lowest', N)
    alen=[len(c),len(h),len(l)]
    if alen[0] > 0 and alen[1] > 0 and alen[2] > 0:
        size = min(alen[0],alen[1],alen[2])
        return True, sat_math.List2npArray(c[:size]),sat_math.List2npArray(h[:size]),sat_math.List2npArray(l[:size])
    return False,None,None,None
    
#短期最高点，最低点;中期最高点，最低点;长期最高点，最低点。
def ArrHL(lp):
    lShortH = []
    lShortL = []
    if (len(lp) < 3):
        return False,None,None

    for i in range(1, len(lp)-1):
        if (lp[i] > lp[i-1] and lp[i] > lp[i+1]):
            lShortH.append((i, lp[i]))
        if (lp[i] < lp[i-1] and lp[i] < lp[i+1]):
            lShortL.append((i, lp[i]))

    return True,lShortH,lShortL

def TestHL():
    code='600586'
    b,u = GetDataByCodeIndi(code,'cur', -1)
    if b == True:
        b,lH,lL=ArrHL(u)
        if (debug):
            print(code, 'HighPoints,LowPoints','\n', lH[:5],'\n',lL[:5])

    
##Outside envelope
#def ArrOutside(c,h,l):
#    if c.size < 2:
#        return False, None
#    for i in range (0, c.size):
#        
#
#def TestOutside():
#    code='600586'
#    b,u = GetDataByCodeIndi(code,'cur', -1)
#    if b == True:
#        b,lH,lL=ArrHL(u)
#        if (debug):
#            print(code, 'HighPoints,LowPoints','\n', lH[:5],'\n',lL[:5])
#

#5、成交量型
#包括：ADVOL、成交值、负量指标、OBV、正量指标、PVT、成交量、SSL、邱氏量法、成本分布。
#成交量型有N字波动型和O轴穿越型。信号发生的标志有：

#VOL
def VOL(lv, N=5):
    return MA(lv,N)
def ArrVOL(lv,N=5):
    return ArrMA(lv,N)

#6、均线型 DONE
#包括：BBI、EXPMA、MA、VMA、HMA、LMA。
#即各种不同算法的平均线。主要通过短期均线穿越长期均线的结果，判断是否为买卖信号。

#多空指标（BBI）的计算公式
#3日均价＝3日收盘价之和/3
#6日均价＝6日收盘价之和/6
#12日均价＝12日收盘价之和/12
#24日均价＝24日收盘价之和/24
#BBI=（3日均价＋6日均价＋12日均价＋24日均价）/4
def BBI(lp, N1=3,N2=6,N3=12,N4=24):
    if lp.size < 1:
        return False, 0
    sum = (lp[0:N1]).mean()
    sum += (lp[0:N2]).mean()
    sum += (lp[0:N3]).mean()
    sum += (lp[0:N4]).mean()
    return True,sum/4

def ArrBBI(lp,N1=3,N2=6,N3=12,N4=24):
    n = lp.size
    size = n - N4 + 1
    if size < 1:
        return False,None
    lret=sat_math.np.zeros(size)
    tmpSum=0.0
    for i in range(0, size):
        tmpSum = (lp[i:i+N1]).mean()
        tmpSum += (lp[i:i+N2]).mean()
        tmpSum += (lp[i:i+N3]).mean()
        tmpSum += (lp[i:i+N4]).mean()
        lret[i]=tmpSum/4
    return True, lret
"""
EBBI＝(6日EMA＋18日EMA＋54日EMA＋162日EMA)÷4
EBBI的应用技巧：
1、EBBI的最大优点在于能及时捕捉长线黑马，当股价处于低位区时，BBI由下向上突破EBBI为长线买入信号。判断上穿有效性的标准要看BBI是从远低于EBBI的位置有力上穿的，还是BBI逐渐走高后与EBBI粘合过程中偶然高于EBBI的，如是后者上穿无效。虽然这个买入信号不能保证买入的股一定100％的成为大黑马，但纵观沪深两市的所有大黑马，几乎全部在低位发出了BBI上穿EBBI的买入信号，所以，不再举例。
2、EBBI的优点并不止是买入信号，还在于它的趋势判断上，如果BBI始终在EBBI之上时，表示股价处于强势状态，可以继续持股，是骑稳黑马的有力工具。如果BBI始终在EBBI之下时，表示股价处于弱势状态，可以继续持币，投资者可对比自己手中的股就会发现EBBI会指示你从2200点直到今年1月都持币。
3、EBBI虽然是优秀的指标，但不是万能的，它只是在某些方面为你提供方便的一种工具，和所有的工具一样，只能在特定的方面发挥长处，就像你不能用勺子去切菜，不能用刀去炒菜一样，EBBI也不能用于对短线趋势的研判，它非常适合于长线投资者。
4、EBBI对于卖出信号的研判也是其缺点之一千万不要简单的推理BBI上穿EBBI为长线买入信号，那么BBI下穿EBBI为长线卖出信号，如果这样，就大错特错了，当BBI下穿EBBI时股价早已失去半壁江山。如果EBBI始终处于递增过程中，可以坚定持股，如果EBBI一旦拐头，就要小心，这时不一定是头部，但要结合其它指标加以确认。
"""    
#1.N日HMA=N日高价之和/N
#2.须设置多条平均线，参数分别为N1=5,N2=14,N3=30,N4=72,N5=144
#MA N=5,10(short),30,60(middle),120,240(long),
#MA,HMA,LMA 同一个算法，都是MA，只是lp的来源不同，分别为cur,highest,lowest
def MA(lp, N=5):
    if lp.size < 1:
        return False,None
    return True, (lp[0:N]).mean()

#返回数组，返回所有的平均点
def ArrMA(lp, N=5):
    n = lp.size
    size = n - N +1
    if size < 1:
        return False,None
    lret=sat_math.np.zeros(size)
    for i in range(0, size):
        lret[i]=(lp[i:N+i]).mean()
    return True,lret

def ArrSum(ls, N=5):
    size = ls.size - N + 1
    if size < 1:
        return False,None
    lret=sat_math.np.zeros(size)
    for i in range(0, size):
        lret[i]=(ls[i:N+i]).sum()
    return True,lret
    
#变异平均线（VMA）与移动平均线的计算方法是一样的，区别在于移动平均线是以每日收盘价计算的，而变异平均线则是用每日的开盘价、收盘价、最高价和最低价相加后除以4得出的数据计算平均线。
"""
HF=（开盘价+收盘价+最高价+最低价）/4
2.VMA=HF的M日简单移动平均线
VMA1=HF的M1日简单移动平均
VMA2=HF的M2日简单移动平均
VMA3=HF的M3日简单移动平均
VMA4=HF的M4日简单移动平均
VMA5=HF的M5日简单移动平均
3.参数M1=6,M2=12,M3=30,M4=72,M5=144
"""  
def VMA(o,c,h,l,N=6):
    n = o.size
    if n < N:
        return False,None
    lHF = sat_math.np.zeros(N)
    for i in range(0, N):
        lHF[i] = (o[i]+c[i]+h[i]+l[i])/4
    return True,lHF.mean()

def ArrVMA(o,c,h,l,N=6):
    n = o.size
    if n < N:
        return False,None
    lHF=sat_math.np.zeros(n)
    for i in range(0, n):
        lHF[i] = (o[i]+c[i]+h[i]+l[i])/4
    return ArrMA(lHF,N)

#EXPMA指标简称EMA，中文名字：指数平均数指标或指数平滑移动平均线，一种趋向类指标
#EXPMA指标参数默认为（12，50），客观讲有较高的使用价值。而经过技术分析人士的研究，发现（6，35）与（10，60）有更好的实战效果。EXPMA指标比较适合与SAR指标配合使用。
#EMA（Exponential Moving Average
#EMAtoday=α * Pricetoday + ( 1 - α ) * EMAyesterday;
#EMAtoday=α * ( Pricetoday - EMAyesterday ) + EMAyesterday;
#通常情况下取EMA1为Price1另外有的技术是将EMA1取值为开头4到5个数值的均值。
#做成非递归 N=12,26
#x = p1+(1-a)p2(yesterday)+((1-a)**2)*p3
#y = 1/a=1+(1-a)+(1-a)**2+...+(1-a)**n-1
#z = x/y
def EMA(lp, N=12):
    n = lp.size
    if n < 6:
        return False, None
    a = 2/(N+1)
    b = 1-a
    ema1 = lp[n-5:n].mean()
    x = lp[0]
    y = 1.0
    tmp = 1.0
    for i in range(1, n):
        tmp *= b
        x += tmp*lp[i]
        y += tmp
    return True,x/y

# 加权因子*当天的收盘价+（1-加权因子）*昨天的EMA
# Test Done , 对比同花顺
def ArrEMA(lp, N=12):
    n = lp.size
    if n < 6:
        return False, None
    a=2/(N+1)
    b=1-a
    ema1 = lp[n-1]
    lret=sat_math.np.zeros(n)
    lret[n-1]=ema1
    for i in range(n-2, -1, -1):
        lret[i] = a*lp[i] + b*lret[i+1]
    return True,lret
  
def TestEMA():
    code='600586'
    b,u = GetDataByCodeIndi(code,'cur', -1)
    N1=12
    N2=26
    if b == True:
        b,ret12=EMA(u, N1)
        b,retMa=MA(u,N1)
        b,arrEMA=ArrEMA(u, N1)
        b,arrEMA2=ArrEMA(u, 10)
        if (debug):
            print(code, 'N=', N1, ' EMA12=', ret12, 'MA=', retMa)
            print('arr ema', len(arrEMA), arrEMA,arrEMA2)

   
#3、趋势型
#包括：ASI、CHAIKIN、DMA、DMI、DPO、EMV、MACD、TRIX、终极指标、VHF、VPT、钱龙长线、钱龙短线、WVAD
#本类型指标至少有两条线，指标以两条线交叉为信号：
#趋向类指标的讯号发生，大致上都是以两条线的交叉为准，把握这个重点就可以运用自如。
#让利润充分增长，限制损失。（Let profit run,Cut lose）真实反映。

#MACD称为指数平滑异同平均线，是从双指数移动平均线发展而来的，由快的指数移动平均线（EMA）减去慢的指数移动平均线，MACD的意义和双移动平均线基本相同，但阅读起来更方便。
#当MACD从负数转向正数，是买的信号。当MACD从正数转向负数，是卖的信号。
#当MACD以大角度变化，表示快的移动平均线和慢的移动平均线的差距非常迅速的拉开，代表了一个市场大趋势的转变。
#DIFF=EMA(close，12）-EMA（close，26）
#再计算DIFF的M日的平均的指数平滑移动平均线，记为DEA。
#最后用DIFF减DEA，得MACD。MACD通常绘制成围绕零轴线波动的柱形图。
#指数平滑异同移动平均线（Moving Average Convergence / Divergence，MACD）
def MACD(lp, FastN, SlowN, M=9):
    bF,lEMAFast = ArrEMA(lp,FastN)
    bS,lEMASlow = ArrEMA(lp,SlowN)
    if bF and bS:
        emaSize=lEMAFast.size
        if emaSize < 1:
            return False,None,None,None
        ldiff=sat_math.np.zeros(emaSize)
        for i in range(0, emaSize):
            ldiff[i]= lEMAFast[i]-lEMASlow[i]
        b,dea=EMA(ldiff, M)   
        if b:     
            return True,(ldiff[0]-dea)*2,ldiff[0],dea
    return False,None,None,None
 
def ArrMACD(lp, FastN, SlowN, M=9):
    bF,lEMAFast = ArrEMA(lp,FastN)
    bS,lEMASlow = ArrEMA(lp,SlowN)
    if bF and bS:
        emaSize=lEMAFast.size
        ldiff=sat_math.np.zeros(emaSize)
        if emaSize < 1:
            return False,None,None,None
        for i in range(0, emaSize):
            ldiff[i]= lEMAFast[i]-lEMASlow[i]
        b,ldea=ArrEMA(ldiff, M)
        if b and ldea.size > 1:
            deaSize = ldea.size
            lret = sat_math.np.zeros(deaSize)
            for i in range(0, deaSize):
                lret[i] = (ldiff[i] - ldea[i])*2
            return True,lret,ldiff,ldea
    return False,None,None,None
 
def TestMACD():
    code='600586'
    b,u = GetDataByCodeIndi(code,'cur', -1)
    N1=12
    N2=26
    M=9
    if b == True:
        b,ret,dif,dea=MACD(u,N1,N2,M)
        b,lret,ldif,ldea=ArrMACD(u,N1,N2,M)
        lsize=[lret.size,ldif.size,ldea.size]
        if (debug):
            print(code, 'N1,N2,M=', N1,N2,M)
            print('macd,dif,dea','\n', ret,'\n',dif,'\n',dea)
            print('lmacd,ldif,lea',lsize, '\n',lret[:30],'\n',ldif[:30],'\n',ldea[:30])
   
'''
TR1:=EMA(MAX(MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1))),ABS(REF(CLOSE,1)-LOW)),N);
HD :=HIGH-REF(HIGH,1);
LD :=REF(LOW,1)-LOW;
DMP:=EMA(IF(HD>0 AND HD>LD,HD,0),N);
DMM:=EMA(IF(LD>0 AND LD>HD,LD,0),N);
PDI:= DMP*100/TR1;
MDI:= DMM*100/TR1;
ADX: EMA((PDI-MDI)/(MDI+PDI)*100,M)*2;
ADXR:EMA(ADX,M);
ADMA:EMA(ADX,M1);

OMD:(ADX-2*ADMA+ADXR)/2, COLORSTICK;
DRAWBAND(ADX,RGB(155,50,50),ADXR,RGB(0,100,50));
STICKLINE(OMD>REF(OMD,1) AND OMD>0,0,OMD,1,0),colorred;
STICKLINE(OMD>REF(OMD,1) AND OMD<0,0,OMD,1,0),colorgreen;
STICKLINE(OMD<REF(OMD,1),0,OMD,1,0),COLORCBCBC0;
STICKLINE(OMD>=0 OR OMD<=0,0,0,50,1),colorwhite;
'''
def DMI_TR1_Para(c, h, l):
    if c.size < 2:
        return False, None

    lret = sat_math.np.zeros(c.size - 1)
    for i in range(0, c.size - 1):
        lret[i] = max(h[i]-l[i], abs(h[i]- c[i+1]), abs(c[i+1] - l[i]))
    return True, lret

def DMI_DMPDMM_Para(h, l):
    if h.size < 2:
        return False, None, None

    lDmpPara = sat_math.np.zeros(h.size - 1)
    lDmmPara = sat_math.np.zeros(h.size - 1)
    for i in range(0, h.size - 1):
        hd = h[i] - h[i+1]
        ld = l[i+1] - l[i]
        if hd > ld:
            ld = 0
            hd = max(hd, 0)
        else:
            hd = 0
            ld = max(ld, 0)

        lDmpPara[i] = hd
        lDmmPara[i] = ld
    return True, lDmpPara, lDmmPara

#DMI指标可以用作买卖讯号，也可辨别行情是否已经发动。但必须注意，当市场的上升（下跌）趋势非常明显时，利用该指标进行买卖指导效果较好，当市场处于盘整时，该指标会失真
#PDI:= DMP*100/TR1;
#MDI:= DMM*100/TR1;
#ADX: EMA((PDI-MDI)/(MDI+PDI)*100,M)*2;
#ADXR:EMA(ADX,M);
#ADMA:EMA(ADX,M1);
#
def DMI(c, h, l, N=14, M=6, M1=14):
    bTr1Para, lTr1Para = DMI_TR1_Para(c, h, l)
    if not bTr1Para:
        return False, None, None, None, None,None
    bTr1, lTr1 = ArrEMA(lTr1Para, N)
    if not bTr1:
        return False, None, None, None, None,None
    bDmPara, lDmpPara, lDmmPara = DMI_DMPDMM_Para(h, l)
    bDmp, lDmp = ArrEMA(lDmpPara, N)
    bDmm, lDmm = ArrEMA(lDmmPara, N)
    if (not bDmp) or  (not bDmm):
        return False, None, None, None, None,None
    size = min(lTr1.size, lDmp.size, lDmm.size)

    lPdi = sat_math.np.zeros(size)
    lMdi = sat_math.np.zeros(size)
    lAdxPara = sat_math.np.zeros(size)
    for i in range(0, size):
        lPdi[i] = (lDmp[i] * 100) / lTr1[i]
        lMdi[i] = (lDmm[i] * 100) / lTr1[i]
        if (lPdi[i]+lMdi[i]) != 0.0:
            lAdxPara[i] = abs(((lPdi[i] - lMdi[i]) / (lPdi[i] + lMdi[i])) * 100) #modify DX 运算结果取其绝对值，再将 DX 作移动平均，得到 ADX。
        else:
            lAdxPara[i] = 0
    bAdx, lAdx = ArrEMA(lAdxPara, M)
    for j in range(0, lAdx.size):
        lAdx[j] = lAdx[j] * 2

    bAdxr, Adxr = EMA(lAdx, M) #M
    bAdxm, Adxm = EMA(lAdx, M1) #M1
    return True, lPdi[0], lMdi[0], lAdx[0], Adxr, Adxm     

def ArrDMI(c, h, l, N=14, M=6, M1=14):
    bTr1Para, lTr1Para = DMI_TR1_Para(c, h, l)
    if not bTr1Para:
        return False, None, None,None,None,None
    bTr1, lTr1 = ArrEMA(lTr1Para, N)
    if not bTr1:
        return False, None, None, None, None,None
    bDmPara, lDmpPara, lDmmPara = DMI_DMPDMM_Para(h, l)
    bDmp, lDmp = ArrEMA(lDmpPara, N)
    bDmm, lDmm = ArrEMA(lDmmPara, N)
    if (not bDmp) or (not bDmm):    
        return False, None, None, None, None,None
    size = min(lTr1.size, lDmp.size, lDmm.size)
    lPdi = sat_math.np.zeros(size)
    lMdi = sat_math.np.zeros(size)
    lAdxPara = sat_math.np.zeros(size)
    for i in range(0, size):
        if lTr1[i] != 0.0:
            lPdi[i] = (lDmp[i] * 100) / lTr1[i]
            lMdi[i] = (lDmm[i] * 100) / lTr1[i]
        if (lPdi[i]+lMdi[i]) != 0.0:
            lAdxPara[i] = abs(((lPdi[i] - lMdi[i]) / (lPdi[i] + lMdi[i])) * 100) #modify
        else:
            lAdxPara[i] = 0#modify by lzw
    bAdx, lAdx = ArrEMA(lAdxPara, M)
    for j in range(0, lAdx.size):
        lAdx[j] = lAdx[j] #* 2

    bAdxr, lAdxr = ArrEMA(lAdx, M)
    bAdxm, lAdxm = ArrEMA(lAdx, M1)
    return True, lPdi, lMdi, lAdx, lAdxr, lAdxm

def TestDMI():
    code='000001'
    b,c,h,l = GetCHLDataByCode(code, -1)
    N=14
    M=6
    M1=14
    if b == True:
        #b,pdi,mdi,adx,adxr,adxm=DMI(c, h, l, N, M, M1)
        b,lpdi,lmdi,ladx,ladxr,ladxm=ArrDMI(c, h, l, N, M, M1)
        lsize=[lpdi.size,lmdi.size,ladx.size,ladxr.size,ladxm.size]
        print(code, 'N,M,M1=', N,M,M1)
        #print('pdi,mdi,adx,adxr,adxm','\n', pdi,'\n',mdi,'\n',adx,'\n',adxr,'\n',adxm)
        showSize = 5
        print('lpdi,lmdi,ladx,ladxr,ladxm',lsize, '\n',lpdi[:showSize],'\n',lmdi[:showSize],'\n',ladx[:showSize],'\n',ladxr[:showSize],'\n',ladxm[:showSize])


#2、超买超卖型 Over Bought Over Sold
#包括：CCI、DRF、KDJ、K%R、KAIRI、MFI、MOM、OSC、QIANLONG、ROC、RSI、SLOWKD、VDL、W%R、BIAS、BIAS36、布林极限、极限宽。  
#ROC,WR,KDJ 
#rate of change N=5,12,25
def ROC(lp, N=12):
    n = lp.size
    if n < N:
        return False,None
    u = ((lp[0] - lp[N-1])/lp[N-1])*100
    return True,u
    
def ArrROC(lp, N=12):
    n = lp.size
    sizeROC = n - N + 1
    if sizeROC < 1:
        return False,None
    lret = sat_math.np.zeros(sizeROC)
    for i in range(0, sizeROC):
        tmp=lp[i+N-1]
        if tmp != 0.0:
            lret[i]=((lp[i]-tmp)/tmp)*100
        else:
            lret[i]=50
    return True,lret

def ROCMA(lp, N=12, M=6):
    b,lroc=ArrROC(lp,N)
    b,lma=ArrMA(lp,M)
    if b:
        #if (debug): print("roc,rocma:", u, '\n', lret)
        return True,lma[0],lma.max(),lma.min()
    return False,None,None,None
    
def ArrROCMA(lp, N=12, M=6):
    n = lp.size
    if n < N:
        return False,None
    b,u=ArrROC(lp,N)
    b,lret=ArrMA(lp,M)
    #if (debug): print("roc,rocma:", u, '\n', lret)
    return b,lret
    
def TestROC():
    code='600000'#'601818'600586
    ind = 'cur'
    b, u = GetDataByCodeIndi(code,ind, -1)
    if b == True:
        b,roc = ROC(u, 12)
        b,speed,max,min = ROCMA(u,12, 6)
        b,aroc=ArrROC(u,12)
        b,lspeed=ArrROCMA(u,12,6)
        print('done test roc', code, 'newprice',u[0], roc, 'rocma avg,max,min', speed,max,min)
        print('aroc', aroc.size, aroc[:30])
        print('lspeed', lspeed.size,lspeed[:30])


#未成熟随机值 row stochastic value
#RSV=(closed-lowest(N)) / (highest(N) - lowest(N))*100
def RSV(c,h,l,N=9):
    minM=l[:N].min()
    maxM=h[:N].max()
    if (maxM - minM) <= 0:
        return False,None
    return True,((c[0]-minM)/(maxM-minM))*100

def ArrRSV(c,h,l,N=9):
    size=c.size-N+1
    if size < 1:
        return False,None
    lret=sat_math.np.zeros(size)
    for i in range(0, size):
        minM=l[i:i+N].min()
        maxM=h[i:i+N].max()
        if maxM - minM > 0.0:
            lret[i]=((c[i]-minM)/(maxM-minM))*100
        else:
            lret[i]=50#一般作为无参考意义
    return True,lret

def TestRSV():
    code='002258'#'601818'600586
    b,c,h,l=GetCHLDataByCode(code,-1)
    if b==True:
        b,ret=RSV(c,h,l)
        b,lret=ArrRSV(c,h,l)
        if (debug): print('rsv,lrsv',ret, lret)

#W&R=2n（Hn—C）÷（Hn—Ln）×100
#W&R N=6,10,14,20,70
def WR(c,h,l, N=14):
    minM=l[:N].min()
    maxM=h[:N].max()
    if maxM-minM <= 0:
        return False,None
    return True,((maxM-c[0])/(maxM-minM))*100

def ArrWR(c,h,l, N=14):
    size=c.size-N+1
    if size < 1:
        return False,None
    lret=sat_math.np.zeros(size)
    for i in range(0, size):
        minM=l[i:i+N].min()
        maxM=h[i:i+N].max()
        if maxM - minM > 0.0:
            lret[i]=((maxM-c[i])/(maxM-minM))*100
        else:
            lret[i]=50#一般作为无参考意义
    return True,lret

#
def TestWR():
    code='002510'#'601818'600586
    ind = 'cur'
    b,c,h,l=GetCHLDataByCode(code,100)
    #N=14
    for i in range(2, 100):
        if b==True:
            b,ret=WR(c,h,l,i)
            b,lret=ArrWR(c,h,l,i)
            if (debug): print('wr',ret)
            if b:
                if (ret <= 20): 
                    print("sell")
                elif (ret >= 80): 
                    prisatnt('buy')
                else: 
                    print("Nothing and waiting")
                print("interval_day", i, ' lwr',lret[:30],)


#KDJ  参数N,M1,M2 9,3,3
#K=AVG(RSV-M1)
#D=AVG(RSV-M2)
#J=3*K-2*D 
#SKDJ 慢速,参数N=9,M=3
#RSV2=RSV的M日指数移动平均
#K=AVG(RSV2-M)
#D=AVG(K-M)
#J=3*K-2*D
#K,D (0,100) D > 70(80) sell, D < 30(20) buy(超卖）
#K > D up, buy; K < D down, sell
def KD(c,h,l, N=9,M1=3,M2=3):
    b,lrsv = ArrRSV(c,h,l,N)
    if b and lrsv.size > 1:
        sizeRSV=lrsv.size
        bk,lK=ArrEMA(lrsv, M1)
        if bk:
            bd,D=EMA(lK,M2)
            if bd:
                return True,lK[0],D
    return False,None,None

def ArrKD(c,h,l,N=9,M1=3,M2=3):
    b,lrsv = ArrRSV(c,h,l,N)
    if b and lrsv.size > 1:
        bk,lK=ArrEMA(lrsv,M1)
        if bk:
            bd,lD=ArrEMA(lK,M2)
            if bd:
                return True,lK,lD
    return False,None,None

def KD2(c,h,l, N=9,M1=3,M2=3):
    b,lrsv = ArrRSV(c,h,l,N)
    if b and lrsv.size >= 1:
        sizeRSV=lrsv.size
        bk,lK=ArrMA(lrsv, M1)
        if bk:
            bd,D=MA(lK,M2)
            return bd,lK[0],D
    return False,None,None

def ArrKD2(c,h,l,N=9,M1=3,M2=3):
    b,lrsv = ArrRSV(c,h,l,N)
    if b and lrsv.size >= 1:
        bk,lK=ArrMA(lrsv,M1)
        if bk:
            bd,lD=ArrMA(lK,M2)
            if bd:
                return True,lK,lD
    return False,None,None

        
def KDJ(c,h,l,N=9,M1=3,M2=3):
    b,K,D=KD(c,h,l,N,M1,M2)
    if b:
        J=3*D-2*K #or 3*K-2*D or K-D
        return True,K,D,J
    return False,None,None,None

def ArrKDJ(c,h,l,N=9,M1=3,M2=3):
    b,lK,lD=ArrKD(c,h,l,N,M1,M2)
    if b and lD.size >=1:
        size = lD.size
        lJ=sat_math.np.zeros(size)
        for i in range(0, size):
            lJ[i]=3*lK[i]-2*lD[i]
        return True,lK,lD,lJ
    return False,None,None,None

def TestKDJ():
    code='000001'#'601818'600586
    b,c,h,l=GetCHLDataByCode(code,100)
    if b==True:
        b,k,d=KD(c,h,l)
        b,k2,d2=KD2(c,h,l)
        b,k3,d3,j3=KDJ(c,h,l)
        b,lk,ld=ArrKD(c,h,l)
        b,lk2,ld2=ArrKD2(c,h,l)
        b,lk3,ld3,lj3=ArrKDJ(c,h,l)
        print("kd", k,d,'kd2',k2,d2,'kdj3',k3,d3,j3)
        print('lk,ld','\n',lk[:10],'\n',ld[:10])
        print('lk2,ld2','\n',lk2[:10],'\n',ld2[:10])
        print('lk3,ld3,lj3','\n',lk3[:10],'\n',ld3[:10],'\n',lj3[:10])

"""
顺势指标CCI也包括日CCI指标、周CCI指标、年CCI指标以及分钟CCI指标等很多种类型。经常被用于股市研判的是日CCI指标和周CCI指标。虽然它们计算时取值有所不同，但基本方法一样。
以日CCI计算为例，其计算方法有两种。
第一种计算过程如下：
CCI（N日）=（TP－MA）÷MD÷0.015
其中，TP=（最高价+最低价+收盘价）÷3
MA=近N日收盘价的累计之和÷N
MD=近N日（MA－收盘价）的绝对值累计之和÷N
0.015为计算系数，N为计算周期
"""
#适用短期内暴涨暴跌的非常态行情
def CCI(c,h,l,N=5):
    if c.size < 1:
        return False,None
    tp=(c[0]+h[0]+l[0])/3
    b,lma=ArrMA(c,N)
    if b and lma.size >= N:
        ma=lma[0]
        lmd = sat_math.np.zeros(N)
        for i in range(0,N):
            lmd[i]=sat_math.np.abs(lma[i]-c[i])
        md=lmd.mean()
        return True,(tp-ma)/md/0.015
    return False,None

def ArrCCI(c,h,l,N=14):
    size=c.size
    if size < 1:
        return False,None
    ltp=sat_math.np.zeros(size)
    for i in range(0, size):
        ltp[i]=(c[i]+h[i]+l[i])/3
    b,lma=ArrMA(c,N)
    if b and lma.size >= N:
        sizeMa=lma.size
        ltmpmd = sat_math.np.zeros(sizeMa)
        for i in range(0,sizeMa):
            ltmpmd[i]=sat_math.np.abs(lma[i]-c[i])
        b,lmd=ArrMA(ltmpmd,N)
        if b and lmd.size > 1:
            size=lmd.size
            lret=sat_math.np.zeros(size)
            for i in range(0, size):
                if lmd[i] != 0.0:
                    lret[i] = (ltp[i]-lma[i])/lmd[i]/0.015
                else:
                    lret[i] = 50
            return True,lret
    return False,None

def TestCCI():
    code='600586'#'601818'600586
    b,c,h,l=GetCHLDataByCode(code,100)
    if b==True:
        b,cci=CCI(c,h,l)
        b,lcci=ArrCCI(c,h,l)
        if b:
            print("cci", cci)
            print("lcci",lcci.size,'\n',lcci[:20])

#BIAS 乖离率=[(当日收盘价-N日平均价)/N日平均价]*100%
"""
买进信号：
　　1，当平均线从下降逐渐转为盘局或上升，而价格从平均线下方突破平均线，为买进信号。
　　2、当价格虽跌破平均线，但又立刻回升到平均线上，此时平均线仍然保持上升势态，还为买进信号。
　　3、当价格趋势线走在平均线上，价格下跌并未跌破平均线并且立刻反转上升，亦是买进信号。
　　4、当价格突然暴跌，跌破平均线，且远离平均线，则有可能反弹上升，亦为买进信号。
卖出信号：
　　1、当平均线从上升逐渐转为盘局或下跌，而价格向下跌破平均线，为卖出信号。
　　2、当价格虽然向上突破平均线，但又立刻回跌至平均线以下，此时平均线仍然保持持续下跌势态，还为卖出信号。
　　3、当价格趋势线走在平均线下，价格上升却并未突破平均线且立刻反转下跌，亦是卖出信号。
　　4、当价格突然暴涨，突破平均线，且远离平均线，则有可能反弹回跌，亦为卖出信号。

1．BIAS=(收盘价-收盘价的N日简单平均)/收盘价的N日简单平均*100
2．BIAS指标有三条指标线，N的参数一般设置为6日、12日、24日。
注意：为了指标在大周期（例如，38，57，137，254，526等）运用中更加直观，更加准确把握中期波动，可以将公式进化：
BIAS=(EMA(收盘价，N)-MA(收盘价,M))/MA(收盘价，M)*100;
其中，N取超短周期，例如4，7，9，12等；M为大周期，例如，38，57，137，254，526等；
"""
def BIAS(c, N1=6,N2=12,N3=24):
    if c.size < N1:
        return False, None, None,None
    b1,avg1 = MA(c,N1)
    b2,avg2 = MA(c,N2)
    b3,avg3 = MA(c,N3)
    if b1 and b2 and b3:
        bias1 = ((c[0] - avg1) * 100) / avg1
        bias2 = ((c[0] - avg2) * 100) / avg2
        bias3 = ((c[0] - avg3) * 100) / avg3
        return True,bias1,bias2,bias3
    return False,None,None,None

def ArrBIAS(c, N1=6,N2=12,N3=24):
    size=c.size-N3+1
    if size < 1:
        return False,None,None,None

    lbias1=sat_math.np.zeros(size)
    lbias2=sat_math.np.zeros(size)
    lbias3=sat_math.np.zeros(size)
    b1,b2,b3=False,False,False
    for i in range(0, size):
        b1,avg1 = MA(c[i:], N1)
        b2,avg2 = MA(c[i:], N2)
        b3,avg3 = MA(c[i:], N3)
        if b1 and b2 and b3:
            lbias1[i] = ((c[i] - avg1) * 100) / avg1
            lbias2[i] = ((c[i] - avg2) * 100)/ avg2
            lbias3[i] = ((c[i] - avg3) * 100)/ avg3
        else:
            lbias1[i] = 0
            lbias2[i] = 0
            lbias3[i] = 0
    return True,lbias1,lbias2,lbias3
    
def TestBIAS():
    code='000510'#['000510', '000507', '000022', '000568']
    b,ud=GetDataByCodeIndi(code,'cur')
    if b:
        b,bias1,bias2,bias3=BIAS(ud)
        b,lbias1,lbias2,lbias3=ArrBIAS(ud)
        if b:
            print(code," bias", bias1,bias2,bias3)
            print(code," lbias1,bias2,bias3",lbias1.size,lbias2.size,lbias3.size)
            print('bias1',lbias1)
            print('bias2',lbias2)
            print('bias3',lbias3)


#相对强弱指标：RSI (Relative Strength Index) 强弱指标最早被应用于期货买卖，后来人们发现在众多的图表技术分析中，
#强弱指标的理论和实践极其适合于股票市场的短线投资，于是被用于股票升跌的测量和分析中。
#N日RSI =N日内收盘涨幅的平均值/(N日内收盘涨幅均值+N日内收盘跌幅均值) ×100%
def RSI(lupdown, N=6):
    size=lupdown.size
    if size < N:
        return False,None
    up=sat_math.np.zeros(size)
    down=sat_math.np.zeros(size)
    upCount = 0
    downCount = 0
    for i in range(0, N):
        if (lupdown[i] >= 0.0):
            up[i]=lupdown[i]
            upCount += 1
        else:
            down[i]=0-lupdown[i]
            downCount += 1

    bup,avgUp=MA(up,upCount)
    bdown,avgDown=MA(down,downCount)
    if bup and bdown and (avgUp+avgDown) != 0:
        return True,(avgUp/(avgUp+avgDown))*100
    return False,None

def ArrRSI(lupdown, N=6):
    size=lupdown.size
    if size < N:
        return False,None
    up=sat_math.np.zeros(size)
    down=sat_math.np.zeros(size)
    for i in range(0, size):
        if (lupdown[i] > 0.0):
            up[i]=lupdown[i]
        elif (lupdown[i] < 0.0):
            down[i]=0-lupdown[i]
        else:
            up[i]=0
            down[i]=0
    bu,lavgUp=ArrMA(up,N)
    bd,lavgDown=ArrMA(down,N)
    if bu and bd:
        size = min(lavgUp.size,lavgDown.size)
        if (size < 1):
            return False,None
        lret=sat_math.np.zeros(size)
        for i in range(0, size):
            sum=lavgUp[i]+lavgDown[i]
            if sum != 0.0:
                lret[i]=(lavgUp[i]/(lavgUp[i]+lavgDown[i]))*100
            else:
                lret[i]=50
        return True,lret
    return False,None

def TestRSI():
    code='000826'#'000878'#'601818'600586
    b,ud=GetDataByCodeIndi(code,'cur')
    if b==True:
        lud=sat_math.np.zeros(ud.size-1)
        for i in range(0, ud.size-1):
            lud[i]=ud[i]-ud[i+1]
        b,rsi=RSI(lud)
        b,lrsi=ArrRSI(lud)
        print("rsi", rsi)
        if b:
            print("lrsi",lrsi.size,'\n',lrsi[:20],lrsi.mean(),lrsi.max(),lrsi.min())

#8、选股型
#包括：CSI、DX、PCNT%、TAPI、威力雷达、SV。
#主要用途是用于筛选有投资价值股票的一类指标。

#9、路径型
#包括：布林线、ENVELOPE、MIKE、风林火山。
#也称为压力支撑型。图形区分为上限带和下限带，上限代表压力，下限代表支撑。其指标图形特点是：股价向上触碰上限会回档；股价向下触碰下限会反弹；不同指标有特殊的不同含义。
"""
MID=N天的收盘价的均价；
STD=N天的收盘价的标准差；
UPPER=MID+离差系数*STD；
LOWER=MID-离差系数*STD；
"""
def BOLL(lp, N=14):
    b,mid=MA(lp,N)
    if b:
        std=lp[0:N].std()
        up=mid+2*std
        down=mid-2*std
        return True,mid,up,down
    return False,None,None,None

def ArrBOLL(lp,N=14):
    size=lp.size-N+1
    if (size < 1):
        return False,None,None,None
    b,lmid=ArrMA(lp,N)
    if b:
        lstd=sat_math.np.zeros(size)
        lup=sat_math.np.zeros(size)
        ldown=sat_math.np.zeros(size)
        for i in range(0, size):
            lstd[i]=lp[i:i+N].std()
            lup[i] = lmid[i] + 2*lstd[i]
            ldown[i] = lmid[i] - 2*lstd[i]
        return True,lmid,lup,ldown
    return False,None,None,None
    
def TestBOLL():
    code='000001'#'601818'600586
    b,ud=GetDataByCodeIndi(code,'cur')
    if b:
        b,boll,up,down=BOLL(ud)
        b,lmid,lup,ldown=ArrBOLL(ud)
        if b:
            print("boll", boll,up,down)
            print("lboll:lmid,lup,ldown",lmid.size, lup.size,ldown.size)
            print(lmid,'\n',lup,'\n',ldown)

"""
10、停损型
包括：SAR、VTY。
此类指标不仅具备停损的作用而且具有反转交易的功能，所以，不能单纯以停损的观念看待这个指标，而是一个会产生交易信号的相对独立的交易系统。
股价上涨则停损圈圈（红色）位于股价下方；
股价下跌则停损圈圈（绿色）位于股价上方；
收盘价由下往上突破圈圈（绿色）为买进信号；
收盘价由上往下跌破圈圈（红色）为卖出信号。
SAR指标又叫抛物线指标或停损转向操作点指标，其全称叫“Stop and Reveres，缩写SAR”，是由美国技术分析大师威尔斯-威尔德（Wells Wilder）所创造的，是一种简单易学、比较准确的中短期技术分析工具。
SAR名为停损点，是传统指标中设计形式相当别致的指标。一般的技术指标都是在当天的行情出来后给出当天的指标，指标晚于行情，是追随性的。而SAR是在收到今天的数据后给出明天的停损点，投资人第二天可以在盘中盯着这个点，一旦被突破立刻止损，使人做到"心中有数"保持操作的主动性，可以避免其它指标被动追随的缺点。 
SAR指标的一般研判标准包括以下四个方面： 　
1、当股票股价从SAR曲线下方开始向上突破SAR曲线时，为买入信号，预示着股价一轮上升行情可能展开，投资者应迅速及时地买进股票。 
2、当股票股价向上突破SAR曲线后继续向上运动而SAR曲线也同时向上运动时，表明股价的上涨趋势已经形成，SAR曲线对股价构成强劲的支撑，投资者应坚决持股待涨或逢低加码买进股票。
3、当股票股价从SAR曲线上方开始向下突破SAR曲线时，为卖出信号，预示着股价一轮下跌行情可能展开，投资者应迅速及时地卖出股票。 
4、当股票股价向下突破SAR曲线后继续向下运动而SAR曲线也同时向下运动，表明股价的下跌趋势已经形成，SAR曲线对股价构成巨大的压力，投资者应坚决持币观望或逢高减磅。
SAR指标具有以下优点：[2]
1、操作简单，买卖点明确，出现买卖信号即可进行操作，特别适合于入市时间不长、投资经验不丰富、缺乏买卖技巧的中小投资者使用。 　　2、适合于连续拉升的“牛股”，不会轻易被主力震仓和洗盘。
3、适合于连续阴跌的“熊股”，不会被下跌途中的反弹诱多所蒙骗。
4、适合于中短线的波段操作。 　
5、长期使用SAR指标虽不能买进最低价，也不能卖出最高价，但可以避免长期套牢的危险，同时又能避免错失牛股行情。
SAR（n）=SAR（n－1）+AF * (EP（N-1）－SAR（N-1）)
其中，SAR（n）为第n日的SAR值，SAR（n－1）为第（n－1）日的值
AF为加速因子（或叫加速系数），EP为极点价（最高价或最低价）
AF=0.02~0.2
SAR(0)=lowest(N) or hights(N)
################################
(１)先选定一段时间判断为上涨或下跌。
(２)若是看涨，则第一天的SAR值必须是近期内的最低价；若是看跌，则第一天的SAR须是近期的最高价。
(３)第二天的SAR，则为第一天的最高价(看涨时)或是最低价(看跌时)与第一天的SAR的差距乘上加速因子，再加上第一天的SAR就可求得。
(４)每日的SAR都可用上述方法类推，归纳公式如下:
SAR(n)= SAR(n-1)＋ＡＦ*(EP(n-1)－SAR(n-1))
SAR(n)= 第n日的SAR值，SAR(n-1)即第(n-1)日之值;
AF；加速因子；
EP：极点价，若是看涨一段期间，则EP为这段期间的最高价，若是看跌一段时间，则EP为这段期间的最低价；
EP(n-1)：第(n-1)日的极点价。
(5)加速因子第一次取0.02，假若第一天的最高价比前一天的最高价还高，则加速因子增加0.02，若无新高则加速因子沿用前一天的数值，但加速因子最高不能超过0.2。反之，下跌也类推。
(6)
若是看涨期间，计算出某日的SAR比当日或前一日的最低价高，则应以当日或前一日的最低价为某日之SAR；
若是看跌期间，计算某日之SAR比当日或前一日的最高价低，则应以当日或前一日的最高价为某日的SAR。
"""
def ArrSAR(c,h,l,N=4, step=0.02, maxAF=0.2):
    n = c.size-N
    if (n < 1):
        return False,None
    lret=sat_math.np.zeros(n)
    isLong = True #假设看涨
    ep= 0
    sar= 0
    af=step
    newHigh = h[n:n+N].max()
    newLow = l[n:n+N].min()
    if isLong:
        ep = h[n-1]
        sar = newLow
    else:
        ep = l[n-1]
        sar = newHigh

    newHigh = h[n-1]
    newLow = l[n-1]
    if (debug): print('sar0=', sar, 'lep0=', ep)
    for i in range(n-1, -1, -1):
        prevHigh = newHigh
        prevLow = newLow
        newHigh = h[i] #此处取h[i:i+N].max()还是取h[i]有待确认
        newLow = l[i] #此处取l[i:i+N].min()还是取l[i]有待确认

        if isLong:
            if newLow <= sar:
                isLong = False
                sar = ep
                if sar < prevHigh:
                    sar = prevHigh
                if sar < newHigh:
                    sar = newHigh

                lret[i] = sar

                af = step
                ep = newLow
                sar += (af * (ep - sar))

                if sar < prevHigh:
                    sar = prevHigh
                if sar < newHigh:
                    sar = newHigh                
            else: #no swith
                lret[i] = sar
                if (newHigh > ep):
                    ep = newHigh
                    af += step
                    if (af > maxAF):
                        af = maxAF
                sar += (af * (ep - sar))
                if (sar > prevLow):
                    sar = prevLow
                if (sar > newLow):
                    sar = newLow
        else:
            if (newHigh >= sar):
                isLong = True
                sar = ep
                if (sar > prevLow):
                    sar = prevLow
                if (sar > newLow):
                    sar = newLow
                lret[i] = sar
                af = step
                ep = newHigh
                
                sar += (af * (ep - sar))
                if (sar > prevLow):
                    sar = prevLow
                if (sar > newLow):
                    sar = newLow
            else: #no switch
                lret[i] = sar
                if (newLow < ep):
                    ep = newLow
                    af += step
                    if (af > maxAF):
                        af = maxAF
                sar += (af * (ep - sar))
                if sar < prevHigh:
                    sar = prevHigh
                if sar < newHigh:
                    sar = newHigh
        if (debug): print('i=', i, 'sar=', lret[i], 'ep=', ep, 'af=', af)
    return True,lret

#http://club.1688.com/article/2378091.html
def TestSAR():
    code='300306'#'000959'#'601818'600586
    b,c,h,l=GetCHLDataByCode(code,100)
    if b:
        print('here',c.size)
        b,lsar=ArrSAR(c,h,l)
        if b:
            print("lsar",lsar.size, lsar)
            print("price", c.size, c)


if __name__ == '__main__':
    start = time.time()    #TestEMA()
    code = ['002699', '002528', '002256', '002722', '000927', '000668', '002016', '000889', '002072', '002137', '600794', '200770', '000035', '002301', '002476', '002622', '000800', '200413', '000897', '600038', '002245', '002010', '000010', '002625']
    #TestMACD() #done
    #TestROC()
    #TestRSV()
    #TestWR() #done
    #TestKDJ() #done
    #TestCCI()
    #TestBIAS()
    #TestRSI()
    #TestBOLL()
    #TestSAR()
    TestDMI()
    #TestHL()
    end = time.time()
    print("math total seconds %d" %(end - start))

